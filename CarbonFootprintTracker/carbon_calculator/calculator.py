"""
Carbon Footprint Calculator Module

This module calculates carbon footprints based on various lifestyle factors including:
- Commuting habits
- Dietary choices
- Office-related activities

It uses standardized emission factors to convert activities into CO2 equivalent emissions.
"""

from carbon_calculator.emission_factors import (
    COMMUTE_FACTORS, 
    DIET_FACTORS, 
    OFFICE_FACTORS
)

class CarbonFootprintCalculator:
    """
    A calculator for determining carbon footprints based on lifestyle choices.
    
    Provides methods to calculate emissions from different activities and
    generates an overall carbon footprint score on a 0-100 scale.
    """
    
    def __init__(self):
        """Initialize the calculator with default values."""
        pass
        
    def calculate_commute_emissions(self, distance, mode, car_type=None):
        """
        Calculate emissions from commuting.
        
        Args:
            distance (float): Daily commute distance in miles
            mode (str): Transportation mode (car, bus, train, bike, walk)
            car_type (str, optional): Type of car if mode is car (gas, hybrid, electric)
            
        Returns:
            float: CO2 emissions in kg
        """
        # Default to 0 if distance is None
        if distance is None:
            return 0
            
        # Convert to weekly emissions (5 workdays)
        weekly_distance = distance * 5
        
        # Calculate based on mode of transportation
        if mode == 'car':
            # Different emission factors for different car types
            if car_type == 'electric':
                factor = COMMUTE_FACTORS['car']['electric']
            elif car_type == 'hybrid':
                factor = COMMUTE_FACTORS['car']['hybrid']
            else:  # Default to gas
                factor = COMMUTE_FACTORS['car']['gas']
        elif mode in COMMUTE_FACTORS:
            factor = COMMUTE_FACTORS[mode]
        else:
            # Default for unknown modes (walking, biking, etc.)
            return 0
            
        return weekly_distance * factor
        
    def calculate_diet_emissions(self, diet_type, local_food_percentage):
        """
        Calculate emissions from dietary choices.
        
        Args:
            diet_type (str): Type of diet (omnivore, pescatarian, vegetarian, vegan)
            local_food_percentage (int): Percentage of locally sourced food (0-100)
            
        Returns:
            float: CO2 emissions in kg per week
        """
        if diet_type not in DIET_FACTORS:
            diet_type = 'omnivore'  # Default to omnivore if type not recognized
            
        # Get base emissions for diet type
        base_emissions = DIET_FACTORS[diet_type]
        
        # Adjust for local food percentage (reduce emissions by up to 20% for local food)
        local_adjustment = 1 - (local_food_percentage / 100 * 0.2)
        
        return base_emissions * local_adjustment
        
    def calculate_office_emissions(self, days_per_week, paper_usage, energy_usage):
        """
        Calculate emissions from office-related activities.
        
        Args:
            days_per_week (int): Number of days in office per week
            paper_usage (str): Level of paper usage (low, medium, high)
            energy_usage (str): Level of energy usage (low, medium, high)
            
        Returns:
            float: CO2 emissions in kg per week
        """
        # Default values if None is provided
        if days_per_week is None:
            days_per_week = 0
        if paper_usage not in OFFICE_FACTORS['paper']:
            paper_usage = 'medium'
        if energy_usage not in OFFICE_FACTORS['energy']:
            energy_usage = 'medium'
            
        # Calculate emissions from paper and energy usage
        paper_emissions = OFFICE_FACTORS['paper'][paper_usage]
        energy_emissions = OFFICE_FACTORS['energy'][energy_usage]
        
        # Scale by number of days in office
        total_office_emissions = (paper_emissions + energy_emissions) * days_per_week / 5
        
        return total_office_emissions
        
    def calculate_commute_footprint(self, commute_data):
        """
        Calculate emissions from commuting based on detailed usage patterns.
        
        Args:
            commute_data (dict): Contains distance, days_by_car, days_public_transit, 
                                days_ev, car_type
            
        Returns:
            float: CO2 emissions in kg per week
        """
        distance = commute_data.get('distance', 0)
        days_by_car = commute_data.get('days_by_car', 0)
        days_public_transit = commute_data.get('days_public_transit', 0)
        days_ev = commute_data.get('days_ev', 0)
        car_type = commute_data.get('car_type', 'gas')
        
        # Calculate car emissions
        car_factor = COMMUTE_FACTORS['car']['gas']  # default
        if car_type == 'hybrid':
            car_factor = COMMUTE_FACTORS['car']['hybrid']
        elif car_type == 'electric':
            car_factor = COMMUTE_FACTORS['car']['electric']
            
        car_emissions = distance * days_by_car * car_factor
        
        # Calculate EV emissions
        ev_emissions = distance * days_ev * COMMUTE_FACTORS['car']['electric']
        
        # Calculate public transit emissions
        transit_emissions = distance * days_public_transit * COMMUTE_FACTORS['bus']
        
        # Total weekly emissions (assuming round trip)
        total_emissions = (car_emissions + ev_emissions + transit_emissions) * 2
        
        return total_emissions
        
    def calculate_office_footprint(self, office_data):
        """
        Calculate emissions from office and remote work activities.
        
        Args:
            office_data (dict): Contains remote_days, video_hours, computer_hours,
                              printer_pages, hvac_usage
                              
        Returns:
            float: CO2 emissions in kg per week
        """
        remote_days = office_data.get('remote_days', 0)
        video_hours = office_data.get('video_hours', 0)
        computer_hours = office_data.get('computer_hours', 0)
        printer_pages = office_data.get('printer_pages', 0)
        hvac_usage = office_data.get('hvac_usage', 'medium')
        
        # Calculate emissions from video conferencing
        # Assume 1 hour of video = 0.5 kg CO2
        video_emissions = video_hours * 0.5
        
        # Calculate emissions from computer usage
        # Assume 1 hour of computer = 0.1 kg CO2
        computer_emissions = computer_hours * 0.1
        
        # Calculate emissions from printing
        # Assume 1 page = 0.05 kg CO2
        printer_emissions = printer_pages * 0.05
        
        # Calculate emissions from HVAC
        hvac_factors = {'low': 1.0, 'medium': 2.0, 'high': 3.0}
        hvac_factor = hvac_factors.get(hvac_usage, 2.0)
        # Assume baseline of 2.0 kg CO2 per day for HVAC at medium setting
        hvac_emissions = (5 - remote_days) * hvac_factor
        
        # Calculate remote work savings
        # Assume 30% reduction in emissions for each remote day
        remote_savings = remote_days * 1.5
        
        total_emissions = video_emissions + computer_emissions + printer_emissions + hvac_emissions - remote_savings
        
        # Ensure we don't return negative emissions
        return max(0, total_emissions)
        
    def calculate_travel_footprint(self, travel_data):
        """
        Calculate emissions from business travel.
        
        Args:
            travel_data (dict): Contains air_miles, hotel_nights, rental_car_days
            
        Returns:
            float: CO2 emissions in kg per month
        """
        air_miles = travel_data.get('air_miles', 0)
        hotel_nights = travel_data.get('hotel_nights', 0)
        rental_car_days = travel_data.get('rental_car_days', 0)
        
        # Calculate air travel emissions 
        # Assume 0.2 kg CO2 per mile
        air_emissions = air_miles * 0.2
        
        # Calculate hotel stay emissions
        # Assume 15 kg CO2 per night
        hotel_emissions = hotel_nights * 15
        
        # Calculate rental car emissions
        # Assume 10 kg CO2 per day (average usage)
        car_emissions = rental_car_days * 10
        
        return air_emissions + hotel_emissions + car_emissions
    
    def calculate_footprint_score(self, total_emissions):
        """
        Calculate a score based on total carbon footprint.
        
        Args:
            total_emissions (float): Total carbon emissions in kg CO2
            
        Returns:
            int: A score from 0-100 (100 is best)
        """
        # Convert to score (0-100, lower is better)
        # Assuming 100kg CO2e per week as the baseline for a score of 50
        baseline = 100
        if total_emissions <= 0:
            score = 100  # Perfect score for zero emissions
        elif total_emissions >= 200:
            score = 0    # Worst score for very high emissions
        else:
            # Linear scale from 0-100
            score = max(0, min(100, 100 - (total_emissions / baseline * 50)))
            
        return round(score)
        
    def calculate_total_footprint(self, commute_data, diet_data, office_data):
        """
        Calculate total carbon footprint from all components.
        
        Args:
            commute_data (dict): Contains distance, mode, car_type
            diet_data (dict): Contains diet_type, local_food_percentage
            office_data (dict): Contains days_per_week, paper_usage, energy_usage
            
        Returns:
            dict: Contains total_emissions and footprint_score
        """
        # Calculate emissions from each category
        commute_emissions = self.calculate_commute_emissions(
            commute_data.get('distance'),
            commute_data.get('mode'),
            commute_data.get('car_type')
        )
        
        diet_emissions = self.calculate_diet_emissions(
            diet_data.get('diet_type'),
            diet_data.get('local_food_percentage', 0)
        )
        
        office_emissions = self.calculate_office_emissions(
            office_data.get('days_per_week'),
            office_data.get('paper_usage'),
            office_data.get('energy_usage')
        )
        
        # Total weekly emissions
        total_emissions = commute_emissions + diet_emissions + office_emissions
        
        # Convert to score
        score = self.calculate_footprint_score(total_emissions)
            
        return {
            'total_emissions': round(total_emissions, 2),
            'footprint_score': score
        }
