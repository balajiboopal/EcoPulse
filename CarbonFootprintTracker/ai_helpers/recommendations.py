"""
Recommendations Module

Provides AI-driven personalized recommendations for reducing carbon footprint
based on user profiles and behavior patterns.
"""

class RecommendationEngine:
    """
    Engine for generating personalized carbon reduction recommendations.
    
    Analyzes user data to provide targeted recommendations for improving
    sustainability across different lifestyle categories.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        # Recommendation catalog by category and impact level
        self.recommendations = {
            'commute': {
                'high': [
                    "Switch from a gas car to an electric or hybrid vehicle to reduce emissions by up to 75%.",
                    "Start carpooling with colleagues to share commute emissions and reduce traffic congestion.",
                    "Transition to a 3-day office schedule and work remotely the other days to cut commute emissions."
                ],
                'medium': [
                    "Use public transportation once or twice a week instead of driving.",
                    "Optimize your driving route to reduce miles traveled on your commute.",
                    "Maintain proper tire pressure to improve fuel efficiency by up to 3%."
                ],
                'low': [
                    "Turn off your engine instead of idling when waiting more than 30 seconds.",
                    "Drive at moderate speeds to optimize fuel consumption.",
                    "Reduce AC usage in your vehicle to improve fuel efficiency."
                ]
            },
            'diet': {
                'high': [
                    "Try going meatless for 2-3 days per week to reduce your food carbon footprint by up to 30%.",
                    "Replace beef with chicken or plant-based proteins to significantly reduce emissions.",
                    "Shop at local farmers markets to reduce food transportation emissions."
                ],
                'medium': [
                    "Reduce food waste by planning meals and storing food properly.",
                    "Choose seasonal fruits and vegetables that require less energy for production.",
                    "Buy in bulk to reduce packaging waste and transportation emissions."
                ],
                'low': [
                    "Bring reusable bags when shopping to reduce plastic waste.",
                    "Choose products with minimal packaging when shopping.",
                    "Start a small herb garden to supplement some of your produce needs."
                ]
            },
            'office': {
                'high': [
                    "Switch to digital documentation and implement a paperless workflow.",
                    "Use energy-efficient equipment and turn off devices when not in use.",
                    "Advocate for renewable energy sources for your office building."
                ],
                'medium': [
                    "Print on both sides of paper and use recycled paper products.",
                    "Adjust your thermostat by 1-2 degrees to reduce energy consumption.",
                    "Use natural lighting when possible instead of artificial lighting."
                ],
                'low': [
                    "Use a reusable water bottle and coffee cup at work.",
                    "Power down your computer at the end of the day instead of leaving it on standby.",
                    "Use stairs instead of elevators for short trips between floors."
                ]
            }
        }
    
    def get_personalized_recommendations(self, user_data, limit=3):
        """
        Generate personalized recommendations based on user profile.
        
        Args:
            user_data (dict): User's carbon footprint data
            limit (int): Maximum number of recommendations to return
            
        Returns:
            list: Personalized sustainability recommendations
        """
        recommendations = []
        categories_to_improve = self._identify_improvement_areas(user_data)
        
        # Get recommendations for top categories to improve
        for category, impact in categories_to_improve[:limit]:
            if category in self.recommendations and impact in self.recommendations[category]:
                # Select the first recommendation from the appropriate category and impact level
                recommendations.append({
                    'category': category.capitalize(),
                    'impact_level': impact,
                    'text': self.recommendations[category][impact][0]
                })
                
                # If we don't have enough recommendations yet, add another from the same category
                if len(recommendations) < limit and len(self.recommendations[category][impact]) > 1:
                    recommendations.append({
                        'category': category.capitalize(),
                        'impact_level': impact,
                        'text': self.recommendations[category][impact][1]
                    })
        
        # Fill remaining slots with general recommendations if needed
        while len(recommendations) < limit:
            for category in ['commute', 'diet', 'office']:
                if len(recommendations) < limit:
                    for impact in ['medium', 'low']:
                        if len(recommendations) < limit and self.recommendations[category][impact]:
                            # Check if this recommendation is already included
                            new_rec = {
                                'category': category.capitalize(),
                                'impact_level': impact,
                                'text': self.recommendations[category][impact][0]
                            }
                            if new_rec not in recommendations:
                                recommendations.append(new_rec)
                            
                            if len(recommendations) >= limit:
                                break
                    
                if len(recommendations) >= limit:
                    break
        
        return recommendations[:limit]
    
    def _identify_improvement_areas(self, user_data):
        """
        Identify areas where the user can improve their carbon footprint.
        
        Args:
            user_data (dict): User's carbon footprint data
            
        Returns:
            list: Categories to improve with impact levels, ordered by priority
        """
        improvement_areas = []
        
        # Check commute data
        if user_data.get('commute_mode') == 'car' and user_data.get('car_type') == 'gas':
            improvement_areas.append(('commute', 'high'))
        elif user_data.get('commute_mode') == 'car':
            improvement_areas.append(('commute', 'medium'))
        elif user_data.get('commute_distance', 0) > 20:
            improvement_areas.append(('commute', 'medium'))
        elif user_data.get('commute_distance', 0) > 5:
            improvement_areas.append(('commute', 'low'))
            
        # Check diet data
        if user_data.get('diet_type') == 'omnivore':
            improvement_areas.append(('diet', 'high'))
        elif user_data.get('diet_type') == 'pescatarian':
            improvement_areas.append(('diet', 'medium'))
        elif user_data.get('local_food_percentage', 0) < 30:
            improvement_areas.append(('diet', 'medium'))
        else:
            improvement_areas.append(('diet', 'low'))
            
        # Check office data
        if user_data.get('paper_usage') == 'high' or user_data.get('energy_usage') == 'high':
            improvement_areas.append(('office', 'high'))
        elif user_data.get('paper_usage') == 'medium' or user_data.get('energy_usage') == 'medium':
            improvement_areas.append(('office', 'medium'))
        else:
            improvement_areas.append(('office', 'low'))
            
        # Sort by impact level (high, medium, low)
        impact_priority = {'high': 0, 'medium': 1, 'low': 2}
        improvement_areas.sort(key=lambda x: impact_priority[x[1]])
        
        return improvement_areas
