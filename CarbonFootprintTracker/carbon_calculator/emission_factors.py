"""
Emission Factors Module

Contains standardized emission factors for various activities that contribute
to carbon footprints. All factors are in kg CO2 equivalent.
"""

# Commute emission factors (kg CO2 per mile)
COMMUTE_FACTORS = {
    'car': {
        'gas': 0.41,      # Average gasoline car
        'hybrid': 0.19,   # Hybrid car
        'electric': 0.1   # Electric car (accounting for electricity generation)
    },
    'bus': 0.18,          # Public bus
    'train': 0.12,        # Train or subway
    'motorcycle': 0.22,   # Motorcycle
    'bike': 0,            # Bicycle (zero emissions)
    'walk': 0             # Walking (zero emissions)
}

# Diet emission factors (kg CO2 per week)
DIET_FACTORS = {
    'omnivore': 50,       # Regular meat consumption
    'pescatarian': 30,    # Fish but no meat
    'vegetarian': 20,     # No meat or fish
    'vegan': 10           # No animal products
}

# Office-related emission factors (kg CO2 per week for full-time office work)
OFFICE_FACTORS = {
    'paper': {
        'low': 0.5,       # Minimal paper use
        'medium': 2,      # Average paper use
        'high': 5         # High paper use
    },
    'energy': {
        'low': 5,         # Energy-efficient practices
        'medium': 15,     # Average energy use
        'high': 30        # High energy consumption
    }
}
