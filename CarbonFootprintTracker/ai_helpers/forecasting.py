"""
Forecasting Module

Provides carbon footprint forecasting capabilities based on current data
and predicted changes in behavior.
"""

import datetime

class CarbonForecaster:
    """
    Forecasts future carbon metrics based on current data and potential changes.
    
    Implements a simple heuristic model with configurable reduction targets
    to predict future emissions and potential savings.
    """
    
    def __init__(self, reduction_rate=0.1):
        """
        Initialize the forecaster with a default reduction rate.
        
        Args:
            reduction_rate (float): Expected annual reduction rate (defaults to 10%)
        """
        self.reduction_rate = reduction_rate
    
    def forecast_individual_emissions(self, current_emissions, months=12):
        """
        Forecast individual emissions over time based on current data.
        
        Args:
            current_emissions (float): Current weekly emissions in kg CO2
            months (int): Number of months to forecast
            
        Returns:
            dict: Forecast data including monthly projections and potential savings
        """
        # Convert to annual emissions (52 weeks)
        annual_emissions = current_emissions * 52
        
        # Current month as starting point
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        
        # Calculate monthly reduction rate
        monthly_reduction = self.reduction_rate / 12
        
        # Generate forecast data
        forecast = []
        cumulative_savings = 0
        baseline_annual = annual_emissions
        
        for i in range(months):
            month_num = (current_month + i) % 12
            if month_num == 0:
                month_num = 12
                
            year = current_year + (current_month + i - 1) // 12
            
            # Calculate expected emissions with reductions
            reduction_factor = 1 - (monthly_reduction * i)
            monthly_emissions = (annual_emissions / 12) * reduction_factor
            
            # Calculate baseline (no changes) emissions
            baseline_monthly = baseline_annual / 12
            
            # Calculate savings
            monthly_savings = baseline_monthly - monthly_emissions
            cumulative_savings += monthly_savings
            
            # Add to forecast data
            forecast.append({
                'month': month_num,
                'year': year,
                'emissions': round(monthly_emissions, 2),
                'baseline': round(baseline_monthly, 2),
                'savings': round(monthly_savings, 2),
                'cumulative_savings': round(cumulative_savings, 2)
            })
        
        return {
            'forecast': forecast,
            'total_annual_savings': round(cumulative_savings, 2),
            'reduction_percentage': round(self.reduction_rate * 100, 1)
        }
    
    def forecast_company_emissions(self, employee_data, months=12):
        """
        Forecast company-wide emissions based on employee data.
        
        Args:
            employee_data (list): List of employee emission data
            months (int): Number of months to forecast
            
        Returns:
            dict: Company-wide forecast data
        """
        # Calculate current company emissions (sum of all employees)
        total_current_emissions = sum(emp['total_footprint'] for emp in employee_data)
        
        # Get average emissions per employee
        num_employees = len(employee_data)
        avg_emissions = total_current_emissions / num_employees if num_employees > 0 else 0
        
        # Get individual forecast and scale to company level
        individual_forecast = self.forecast_individual_emissions(avg_emissions, months)
        
        # Scale to company level
        company_forecast = []
        for month_data in individual_forecast['forecast']:
            company_month = month_data.copy()
            company_month['emissions'] = round(month_data['emissions'] * num_employees, 2)
            company_month['baseline'] = round(month_data['baseline'] * num_employees, 2)
            company_month['savings'] = round(month_data['savings'] * num_employees, 2)
            company_month['cumulative_savings'] = round(month_data['cumulative_savings'] * num_employees, 2)
            company_forecast.append(company_month)
        
        # Calculate total potential company savings
        total_company_savings = individual_forecast['total_annual_savings'] * num_employees
        
        return {
            'forecast': company_forecast,
            'total_annual_savings': round(total_company_savings, 2),
            'reduction_percentage': individual_forecast['reduction_percentage'],
            'employee_count': num_employees,
            'average_employee_emissions': round(avg_emissions, 2)
        }
    
    def calculate_reduction_scenarios(self, current_emissions):
        """
        Calculate different reduction scenarios based on varying targets.
        
        Args:
            current_emissions (float): Current weekly emissions in kg CO2
            
        Returns:
            list: Different reduction scenarios with projected outcomes
        """
        # Annual emissions
        annual_emissions = current_emissions * 52
        
        # Define different reduction scenarios
        scenarios = [
            {'name': 'Conservative', 'rate': 0.05, 'description': '5% annual reduction'},
            {'name': 'Moderate', 'rate': 0.1, 'description': '10% annual reduction'},
            {'name': 'Ambitious', 'rate': 0.2, 'description': '20% annual reduction'},
            {'name': 'Aggressive', 'rate': 0.3, 'description': '30% annual reduction'}
        ]
        
        # Calculate outcomes for each scenario
        results = []
        for scenario in scenarios:
            # Calculate 1-year and 5-year emissions
            year1_emissions = annual_emissions * (1 - scenario['rate'])
            year5_emissions = annual_emissions * (1 - scenario['rate'])**5
            
            # Calculate savings
            year1_savings = annual_emissions - year1_emissions
            year5_savings = annual_emissions - year5_emissions
            
            results.append({
                'name': scenario['name'],
                'description': scenario['description'],
                'rate': scenario['rate'],
                'year1_emissions': round(year1_emissions, 2),
                'year5_emissions': round(year5_emissions, 2),
                'year1_savings': round(year1_savings, 2),
                'year5_savings': round(year5_savings, 2),
                'year5_reduction_percentage': round((1 - (1 - scenario['rate'])**5) * 100, 1)
            })
        
        return results
