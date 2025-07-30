#!/usr/bin/env python3
"""
Script to generate test datasets in Excel format for Data Formulator
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def create_sales_data():
    """Create sales dataset with multiple dimensions"""
    np.random.seed(42)
    random.seed(42)
    
    # Generate dates for the last 2 years
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Product categories and products
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    products = {
        'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera'],
        'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Shoes', 'Jacket'],
        'Home & Garden': ['Furniture', 'Kitchen Appliances', 'Garden Tools', 'Decor', 'Lighting'],
        'Sports': ['Basketball', 'Tennis Racket', 'Yoga Mat', 'Running Shoes', 'Gym Equipment'],
        'Books': ['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography']
    }
    
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    data = []
    for date in dates:
        for category in categories:
            for product in products[category]:
                for region in regions:
                    # Generate realistic sales data
                    base_price = random.uniform(20, 500)
                    quantity = np.random.poisson(5)  # Poisson distribution for realistic sales
                    revenue = base_price * quantity
                    
                    # Add some seasonality
                    if date.month in [11, 12]:  # Holiday season
                        quantity = int(quantity * 1.5)
                        revenue = base_price * quantity
                    
                    data.append({
                        'Date': date,
                        'Category': category,
                        'Product': product,
                        'Region': region,
                        'Quantity': quantity,
                        'Unit_Price': round(base_price, 2),
                        'Revenue': round(revenue, 2),
                        'Profit_Margin': round(random.uniform(0.1, 0.4), 2)
                    })
    
    return pd.DataFrame(data)

def create_employee_data():
    """Create employee dataset with various metrics"""
    np.random.seed(42)
    random.seed(42)
    
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    positions = {
        'Engineering': ['Software Engineer', 'Data Scientist', 'DevOps Engineer', 'QA Engineer'],
        'Sales': ['Sales Representative', 'Account Manager', 'Sales Director', 'Business Development'],
        'Marketing': ['Marketing Specialist', 'Content Creator', 'SEO Specialist', 'Brand Manager'],
        'HR': ['HR Coordinator', 'Recruiter', 'HR Manager', 'Benefits Specialist'],
        'Finance': ['Accountant', 'Financial Analyst', 'Controller', 'CFO'],
        'Operations': ['Operations Manager', 'Project Manager', 'Product Manager', 'Scrum Master']
    }
    
    # Generate employee data
    data = []
    for dept in departments:
        for position in positions[dept]:
            num_employees = random.randint(3, 15)
            for i in range(num_employees):
                # Generate realistic employee data
                experience_years = random.randint(0, 20)
                base_salary = {
                    'Engineering': random.uniform(80000, 150000),
                    'Sales': random.uniform(60000, 120000),
                    'Marketing': random.uniform(50000, 100000),
                    'HR': random.uniform(45000, 90000),
                    'Finance': random.uniform(55000, 110000),
                    'Operations': random.uniform(60000, 120000)
                }[dept]
                
                # Adjust salary based on experience
                salary = base_salary * (1 + experience_years * 0.05)
                
                # Performance rating (1-5)
                performance = random.uniform(2.5, 5.0)
                
                # Projects completed
                projects = random.randint(1, 20)
                
                data.append({
                    'Employee_ID': f"EMP{len(data)+1:03d}",
                    'Name': f"Employee {len(data)+1}",
                    'Department': dept,
                    'Position': position,
                    'Experience_Years': experience_years,
                    'Salary': round(salary, 2),
                    'Performance_Rating': round(performance, 1),
                    'Projects_Completed': projects,
                    'Hire_Date': datetime(2020 + random.randint(0, 4), 
                                        random.randint(1, 12), 
                                        random.randint(1, 28))
                })
    
    return pd.DataFrame(data)

def create_weather_data():
    """Create weather dataset with time series data"""
    np.random.seed(42)
    random.seed(42)
    
    # Generate dates for one year
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
    
    data = []
    for date in dates:
        for city in cities:
            # Generate realistic weather data with seasonal patterns
            month = date.month
            
            # Temperature varies by season and city
            if month in [12, 1, 2]:  # Winter
                temp = random.uniform(-10, 15)
            elif month in [3, 4, 5]:  # Spring
                temp = random.uniform(10, 25)
            elif month in [6, 7, 8]:  # Summer
                temp = random.uniform(20, 35)
            else:  # Fall
                temp = random.uniform(10, 25)
            
            # Adjust for city-specific climate
            if city in ['Los Angeles', 'San Diego']:
                temp += 5  # Warmer
            elif city in ['Chicago', 'New York']:
                temp -= 3  # Colder
            
            humidity = random.uniform(30, 80)
            precipitation = random.uniform(0, 50)
            wind_speed = random.uniform(0, 25)
            
            data.append({
                'Date': date,
                'City': city,
                'Temperature_C': round(temp, 1),
                'Humidity_Percent': round(humidity, 1),
                'Precipitation_mm': round(precipitation, 1),
                'Wind_Speed_kmh': round(wind_speed, 1),
                'Weather_Condition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Snowy', 'Partly Cloudy'])
            })
    
    return pd.DataFrame(data)

def create_stock_data():
    """Create stock market dataset"""
    np.random.seed(42)
    random.seed(42)
    
    # Generate dates for one year
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    companies = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA']
    sectors = {
        'AAPL': 'Technology',
        'GOOGL': 'Technology', 
        'MSFT': 'Technology',
        'AMZN': 'Consumer Discretionary',
        'TSLA': 'Consumer Discretionary',
        'META': 'Technology',
        'NFLX': 'Communication Services',
        'NVDA': 'Technology'
    }
    
    data = []
    for company in companies:
        # Start with a realistic base price
        base_price = {
            'AAPL': 150, 'GOOGL': 2800, 'MSFT': 300, 'AMZN': 3300,
            'TSLA': 250, 'META': 350, 'NFLX': 500, 'NVDA': 800
        }[company]
        
        current_price = base_price
        
        for date in dates:
            # Simulate daily price movements
            daily_return = np.random.normal(0, 0.02)  # 2% daily volatility
            current_price *= (1 + daily_return)
            
            # Ensure price doesn't go negative
            current_price = max(current_price, 10)
            
            volume = random.randint(1000000, 10000000)
            
            data.append({
                'Date': date,
                'Symbol': company,
                'Sector': sectors[company],
                'Open_Price': round(current_price * random.uniform(0.98, 1.02), 2),
                'Close_Price': round(current_price, 2),
                'High_Price': round(current_price * random.uniform(1.01, 1.05), 2),
                'Low_Price': round(current_price * random.uniform(0.95, 0.99), 2),
                'Volume': volume,
                'Market_Cap_B': round(current_price * volume / 1000000000, 2)
            })
    
    return pd.DataFrame(data)

def create_customer_survey_data():
    """Create customer satisfaction survey data"""
    np.random.seed(42)
    random.seed(42)
    
    # Generate survey responses
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    product_categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports']
    regions = ['North', 'South', 'East', 'West']
    
    data = []
    for _ in range(1000):  # 1000 survey responses
        age_group = random.choice(age_groups)
        product_category = random.choice(product_categories)
        region = random.choice(regions)
        
        # Generate realistic survey responses
        satisfaction_score = random.randint(1, 10)
        likelihood_to_recommend = random.randint(1, 10)
        purchase_frequency = random.choice(['Monthly', 'Quarterly', 'Yearly', 'First Time'])
        
        # Customer service rating
        customer_service_rating = random.randint(1, 10)
        
        # Price satisfaction
        price_satisfaction = random.randint(1, 10)
        
        # Overall experience
        overall_experience = random.randint(1, 10)
        
        data.append({
            'Response_ID': f"RESP{len(data)+1:04d}",
            'Age_Group': age_group,
            'Product_Category': product_category,
            'Region': region,
            'Satisfaction_Score': satisfaction_score,
            'Likelihood_to_Recommend': likelihood_to_recommend,
            'Purchase_Frequency': purchase_frequency,
            'Customer_Service_Rating': customer_service_rating,
            'Price_Satisfaction': price_satisfaction,
            'Overall_Experience': overall_experience,
            'Survey_Date': datetime(2024, random.randint(1, 12), random.randint(1, 28))
        })
    
    return pd.DataFrame(data)

def main():
    """Generate all test datasets and save to Excel files"""
    
    # Create samples directory if it doesn't exist
    samples_dir = 'samples'
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir)
    
    # Generate datasets
    datasets = {
        'sales_data': create_sales_data(),
        'employee_data': create_employee_data(),
        'weather_data': create_weather_data(),
        'stock_data': create_stock_data(),
        'customer_survey_data': create_customer_survey_data()
    }
    
    # Save each dataset to Excel
    for name, df in datasets.items():
        filename = f"{samples_dir}/{name}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Created {filename} with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample data:\n{df.head(3)}")
        print("-" * 50)
    
    print(f"\nAll test datasets have been created in the '{samples_dir}' folder!")
    print("You can now upload these Excel files to Data Formulator for testing.")

if __name__ == "__main__":
    main() 