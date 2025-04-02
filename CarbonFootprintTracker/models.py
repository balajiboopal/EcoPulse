from app import db
from datetime import datetime

try:
    from flask_login import UserMixin
except ImportError:
    # For tests or environments without flask_login
    class UserMixin:
        @property
        def is_authenticated(self):
            return True
        
        @property
        def is_active(self):
            return True
            
        @property
        def is_anonymous(self):
            return False
            
        def get_id(self):
            return str(self.id)

try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    # Fallback implementations if werkzeug not available
    import hashlib
    import secrets
    
    def generate_password_hash(password):
        """Simple password hashing for fallback."""
        salt = secrets.token_hex(8)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwdhash.hex()}"
    
    def check_password_hash(pwhash, password):
        """Simple password checking for fallback."""
        if not pwhash or '$' not in pwhash:
            return False
        salt, stored_hash = pwhash.split('$', 1)
        calculated_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return secrets.compare_digest(calculated_hash, stored_hash)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    company = db.Column(db.String(128), nullable=True)
    department = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(20), default='employee')  # 'employee' or 'executive'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    footprints = db.relationship('CarbonFootprint', backref='user', lazy=True)
    quiz_scores = db.relationship('QuizScore', backref='user', lazy=True)
    training_progress = db.relationship('TrainingProgress', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CarbonFootprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    
    # Commute data
    commute_days_by_car = db.Column(db.Integer, default=0)  # days per week
    commute_days_public_transit = db.Column(db.Integer, default=0)  # days per week
    commute_days_ev = db.Column(db.Integer, default=0)  # days per week with electric vehicle
    commute_distance = db.Column(db.Float, default=0.0)  # miles per day (one way)
    car_type = db.Column(db.String(50), nullable=True)  # gas, hybrid, electric
    
    # Legacy fields for backward compatibility
    commute_mode = db.Column(db.String(50), default='car')  # car, bus, train, bike, walk
    diet_type = db.Column(db.String(50), default='mixed')  # omnivore, pescatarian, vegetarian, vegan
    local_food_percentage = db.Column(db.Integer, default=50)  # 0-100
    office_days_per_week = db.Column(db.Integer, default=5)  # days per week
    paper_usage = db.Column(db.String(20), default='medium')  # low, medium, high
    energy_usage = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Remote work
    remote_work_days = db.Column(db.Integer, default=0)  # days per week
    video_conference_hours = db.Column(db.Float, default=0.0)  # hours per week
    
    # Business travel
    air_travel_miles = db.Column(db.Float, default=0.0)  # miles per month
    hotel_nights = db.Column(db.Integer, default=0)  # nights per month
    rental_car_days = db.Column(db.Integer, default=0)  # days per month
    
    # Office equipment usage
    computer_hours = db.Column(db.Float, default=0.0)  # hours per day
    printer_pages = db.Column(db.Integer, default=0)  # pages per week
    hvac_usage = db.Column(db.String(50), default='medium')  # low, medium, high
    
    # Card transaction data
    has_transaction_data = db.Column(db.Boolean, default=False)
    transaction_data_period = db.Column(db.String(20), nullable=True)  # 'week', 'month', etc.
    
    # Calculated values
    commute_footprint = db.Column(db.Float, default=0.0)  # kg CO2
    travel_footprint = db.Column(db.Float, default=0.0)  # kg CO2
    office_footprint = db.Column(db.Float, default=0.0)  # kg CO2
    transaction_footprint = db.Column(db.Float, default=0.0)  # kg CO2
    total_footprint = db.Column(db.Float, default=0.0)  # kg CO2
    footprint_score = db.Column(db.Integer, default=0)  # 0-100 scale
    footprint_change = db.Column(db.Float, default=0.0)  # % change from last period
    
    rank_in_company = db.Column(db.Integer, nullable=True)  # Rank among all employees
    rank_in_department = db.Column(db.Integer, nullable=True)  # Rank within department
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class QuizScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer)  # Points scored
    total_possible = db.Column(db.Integer)  # Total possible points
    percentage = db.Column(db.Float)  # Score as percentage
    quiz_date = db.Column(db.DateTime, default=datetime.utcnow)

class SustainabilityTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))  # commute, diet, office, etc.
    tip_text = db.Column(db.Text, nullable=False)
    impact_level = db.Column(db.String(20))  # high, medium, low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CompanyGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)  # Target CO2 reduction in kg
    current_value = db.Column(db.Float, default=0.0)  # Current progress
    deadline = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TrainingProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer)
    module_name = db.Column(db.String(128))
    completion_percentage = db.Column(db.Float, default=0.0)  # 0-100
    completed = db.Column(db.Boolean, default=False)
    certificate_issued = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

class ComplianceStandard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # e.g., 'emissions', 'reporting', 'energy'
    requirements = db.Column(db.Text)
    company_progress = db.Column(db.Float, default=0.0)  # 0-100
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    icon = db.Column(db.String(50), nullable=True)  # Icon identifier for UI
    
class CompanyEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128))
    event_type = db.Column(db.String(50))  # e.g., 'conference', 'workshop', 'team-building'
    attendees_count = db.Column(db.Integer, default=0)
    is_virtual = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='upcoming')  # 'upcoming', 'ongoing', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Carbon footprint related fields
    travel_emissions = db.Column(db.Float, default=0.0)  # kg CO2
    venue_emissions = db.Column(db.Float, default=0.0)  # kg CO2
    accommodation_emissions = db.Column(db.Float, default=0.0)  # kg CO2
    catering_emissions = db.Column(db.Float, default=0.0)  # kg CO2
    materials_emissions = db.Column(db.Float, default=0.0)  # kg CO2
    digital_emissions = db.Column(db.Float, default=0.0)  # kg CO2 (for virtual components)
    total_emissions = db.Column(db.Float, default=0.0)  # kg CO2
    
    # Sustainability metrics
    sustainability_score = db.Column(db.Integer, default=0)  # 0-100
    sustainability_initiatives = db.Column(db.Text)  # JSON formatted list of initiatives
    carbon_offset_percentage = db.Column(db.Float, default=0.0)  # % of emissions offset
    
    # Relationship to event attendees (example if needed in the future)
    # attendees = db.relationship('User', secondary='event_attendees', backref='events')

class TransactionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50))  # e.g., 'travel', 'food', 'utilities'
    merchant = db.Column(db.String(100))
    amount = db.Column(db.Float)
    carbon_impact = db.Column(db.Float)  # Calculated carbon impact in kg CO2
    description = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(50))  # e.g., 'card', 'expense_report', 'manual'
