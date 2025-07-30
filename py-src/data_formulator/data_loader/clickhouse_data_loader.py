# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pandas as pd
import duckdb
from typing import Dict, Any, List
import logging
from data_formulator.data_loader.external_data_loader import ExternalDataLoader, sanitize_table_name

try:
    import clickhouse_connect
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False

logger = logging.getLogger(__name__)

class ClickHouseDataLoader(ExternalDataLoader):
    
    @staticmethod
    def list_params() -> List[Dict[str, Any]]:
        return [
            {
                "name": "host",
                "type": "string",
                "required": True,
                "description": "ClickHouse server hostname or IP address"
            },
            {
                "name": "port",
                "type": "number",
                "required": True,
                "description": "ClickHouse server port (8123 for HTTP, 9000 for native protocol)",
                "default": 8123
            },
            {
                "name": "database",
                "type": "string",
                "required": True,
                "description": "ClickHouse database name"
            },
            {
                "name": "username",
                "type": "string",
                "required": False,
                "description": "ClickHouse username"
            },
            {
                "name": "password",
                "type": "string",
                "required": False,
                "description": "ClickHouse password"
            },
            {
                "name": "secure",
                "type": "boolean",
                "required": False,
                "description": "Use secure connection (HTTPS)",
                "default": False
            },
            {
                "name": "connection_type",
                "type": "string",
                "required": False,
                "description": "Connection type: 'http' or 'native'",
                "default": "http"
            }
        ]
    
    @staticmethod
    def auth_instructions() -> str:
        return """
        ClickHouse Connection Setup:
        
        1. Install the ClickHouse Python client:
           pip install clickhouse-connect
        
        2. Required parameters:
           - host: ClickHouse server hostname or IP
           - port: Server port (8123 for HTTP, 9000 for native)
           - database: Database name to connect to
        
        3. Optional parameters:
           - username/password: For authentication
           - secure: Use HTTPS connection
           - connection_type: 'http' or 'native' protocol
        
        Example connection:
        - host: localhost
        - port: 8123
        - database: default
        - username: default
        - password: (leave empty for no auth)
        """
    
    def __init__(self, params: Dict[str, Any], duck_db_conn: duckdb.DuckDBPyConnection):
        if not CLICKHOUSE_AVAILABLE:
            raise ImportError("clickhouse-connect package is required. Install with: pip install clickhouse-connect")
        
        self.duck_db_conn = duck_db_conn
        
        # Extract connection parameters
        self.host = params.get('host')
        self.port = params.get('port', 8123)
        self.database = params.get('database')
        self.username = params.get('username')
        self.password = params.get('password')
        self.secure = params.get('secure', False)
        self.connection_type = params.get('connection_type', 'http')
        
        if not self.host or not self.database:
            raise ValueError("host and database are required parameters")
        
        # Establish connection
        try:
            if self.connection_type == 'native':
                # For native protocol, use port 9000
                native_port = 9000 if self.port == 8123 else self.port
                self.client = clickhouse_connect.get_client(
                    host=self.host,
                    port=native_port,
                    database=self.database,
                    username=self.username,
                    password=self.password,
                    secure=self.secure
                )
            else:  # HTTP
                # For HTTP protocol, use port 8123
                http_port = 8123 if self.port == 9000 else self.port
                self.client = clickhouse_connect.get_client(
                    host=self.host,
                    port=http_port,
                    database=self.database,
                    username=self.username,
                    password=self.password,
                    secure=self.secure
                )
            
            # Test connection
            self.client.command('SELECT 1')
            logger.info(f"Successfully connected to ClickHouse at {self.host}:{self.port} using {self.connection_type} protocol")
            
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {e}")
            raise
    
    def list_tables(self, table_filter: str = None) -> List[Dict[str, Any]]:
        """List available tables in the ClickHouse database"""
        try:
            # Get list of tables
            query = """
            SELECT 
                name as table_name,
                engine,
                total_rows,
                total_bytes
            FROM system.tables 
            WHERE database = %(database)s
            """
            
            if table_filter:
                query += " AND name ILIKE %(filter)s"
                tables = self.client.query(query, parameters={
                    'database': self.database,
                    'filter': f'%{table_filter}%'
                })
            else:
                tables = self.client.query(query, parameters={'database': self.database})
            
            result = []
            for table in tables.result_rows:
                table_name = table[0]
                full_table_name = f"{self.database}.{table_name}"
                
                # Get column information
                columns_query = f"DESCRIBE {full_table_name}"
                columns = self.client.query(columns_query)
                
                # Format columns to match expected structure
                column_list = []
                for col in columns.result_rows:
                    column_list.append({
                        'name': col[0],
                        'type': col[1]
                    })
                
                # Get sample data (limit to 10 rows)
                sample_query = f"SELECT * FROM {full_table_name} LIMIT 10"
                sample_data = self.client.query(sample_query)
                
                # Convert sample data to list of dictionaries
                sample_rows = []
                if sample_data.result_rows:
                    # Get column names from sample data
                    column_names = [desc[0] for desc in sample_data.column_names]
                    for row in sample_data.result_rows:
                        sample_rows.append(dict(zip(column_names, row)))
                
                # Get row count
                count_query = f"SELECT COUNT(*) FROM {full_table_name}"
                count_result = self.client.query(count_query)
                row_count = count_result.result_rows[0][0] if count_result.result_rows else 0
                
                # Create metadata structure that matches other data loaders
                table_metadata = {
                    "row_count": row_count,
                    "columns": column_list,
                    "sample_rows": sample_rows
                }
                
                result.append({
                    "name": full_table_name,
                    "metadata": table_metadata
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise
    
    def ingest_data(self, table_name: str, name_as: str = None, size: int = 1000000):
        """Ingest data from ClickHouse table into DuckDB"""
        try:
            if name_as is None:
                name_as = sanitize_table_name(table_name)
            
            # Handle table_name format - it might already include database name
            if '.' in table_name:
                # table_name already includes database, use as is
                full_table_name = table_name
            else:
                # table_name is just the table name, add database
                full_table_name = f"{self.database}.{table_name}"
            
            # Build query with size limit
            query = f"SELECT * FROM {full_table_name}"
            if size and size > 0:
                query += f" LIMIT {size}"
            
            logger.info(f"Ingesting data from ClickHouse table '{table_name}' with query: {query}")
            
            # Execute query and get results
            result = self.client.query(query)
            
            # Convert to pandas DataFrame
            # ClickHouse query result has .df() method for newer versions, but let's use the safe approach
            try:
                df = result.df()
            except AttributeError:
                # Fallback for older versions or different result format
                df = pd.DataFrame(result.result_rows, columns=[col[0] for col in result.column_names])
            
            if df.empty:
                logger.warning(f"No data found in table '{table_name}'")
                return
            
            # Ingest into DuckDB
            self.ingest_df_to_duckdb(df, name_as)
            
            logger.info(f"Successfully ingested {len(df)} rows from ClickHouse table '{table_name}' to DuckDB table '{name_as}'")
            
        except Exception as e:
            logger.error(f"Error ingesting data from ClickHouse table '{table_name}': {e}")
            raise
    
    def view_query_sample(self, query: str) -> str:
        """Preview query results without ingesting"""
        try:
            # Add LIMIT to preview
            if 'LIMIT' not in query.upper():
                query += " LIMIT 100"
            
            result = self.client.query(query)
            
            # Convert to pandas DataFrame safely
            try:
                df = result.df()
            except AttributeError:
                df = pd.DataFrame(result.result_rows, columns=[col[0] for col in result.column_names])
            
            if df.empty:
                return "Query returned no results."
            
            # Return sample as formatted string
            sample_str = f"Query returned {len(df)} rows.\n\n"
            sample_str += f"Columns: {list(df.columns)}\n\n"
            sample_str += "Sample data:\n"
            sample_str += df.head(10).to_string()
            
            return sample_str
            
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    def ingest_data_from_query(self, query: str, name_as: str):
        """Ingest data from custom query into DuckDB"""
        try:
            logger.info(f"Ingesting data from custom query to DuckDB table '{name_as}'")
            
            # Execute query
            result = self.client.query(query)
            
            # Convert to pandas DataFrame safely
            try:
                df = result.df()
            except AttributeError:
                df = pd.DataFrame(result.result_rows, columns=[col[0] for col in result.column_names])
            
            if df.empty:
                logger.warning("Query returned no data")
                return
            
            # Ingest into DuckDB
            self.ingest_df_to_duckdb(df, name_as)
            
            logger.info(f"Successfully ingested {len(df)} rows from custom query to DuckDB table '{name_as}'")
            
        except Exception as e:
            logger.error(f"Error ingesting data from custom query: {e}")
            raise 