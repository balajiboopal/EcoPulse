import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development-secret-key")

# Configure database
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # Fix for older SQLAlchemy versions which require postgresql:// instead of postgres://
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:////home/runner/workspace/instance/carbon_footprint.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import routes after app initialization to avoid circular imports
with app.app_context():
    # Import models first to register them with SQLAlchemy
    import models
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.employee import employee_bp
    from routes.company import company_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(company_bp)
    
    # Create all database tables
    db.create_all()
    
    # Add seed data for events only if the table is empty
    from models import CompanyEvent
    from datetime import datetime, timedelta
    import json
    
    if CompanyEvent.query.count() == 0:
        # Create some demo events
        events = [
            {
                'name': 'Annual Sustainability Conference',
                'description': 'Our annual conference bringing together sustainability experts and employees to discuss company initiatives and future goals.',
                'start_date': datetime.now() + timedelta(days=30),
                'end_date': datetime.now() + timedelta(days=32),
                'location': 'Green Convention Center, San Francisco',
                'event_type': 'Conference',
                'attendees_count': 250,
                'is_virtual': False,
                'status': 'upcoming',
                'travel_emissions': 3250.5,
                'venue_emissions': 1200.75,
                'accommodation_emissions': 950.25,
                'catering_emissions': 780.0,
                'materials_emissions': 480.5,
                'digital_emissions': 120.0,
                'total_emissions': 6782.0,
                'sustainability_score': 68,
                'sustainability_initiatives': json.dumps([
                    'Carbon offset purchases for all travel',
                    'Plant-based catering options',
                    'Digital materials instead of printed handouts',
                    'Venue with LEED certification',
                    'Public transportation incentives'
                ]),
                'carbon_offset_percentage': 40.0
            },
            {
                'name': 'Quarterly Team Workshop',
                'description': 'A team-building workshop focused on integrating sustainability into everyday operations.',
                'start_date': datetime.now() + timedelta(days=7),
                'end_date': datetime.now() + timedelta(days=7),
                'location': 'Company Headquarters',
                'event_type': 'Workshop',
                'attendees_count': 35,
                'is_virtual': False,
                'status': 'upcoming',
                'travel_emissions': 280.0,
                'venue_emissions': 150.0,
                'accommodation_emissions': 0.0,
                'catering_emissions': 210.0,
                'materials_emissions': 85.0,
                'digital_emissions': 25.0,
                'total_emissions': 750.0,
                'sustainability_score': 82,
                'sustainability_initiatives': json.dumps([
                    'Zero plastic policy',
                    'Local and organic catering',
                    'Paperless activities',
                    'Energy-efficient venue settings'
                ]),
                'carbon_offset_percentage': 75.0
            },
            {
                'name': 'Virtual Training Series: Carbon Reporting',
                'description': 'A series of online training sessions to help employees understand carbon reporting requirements and methodologies.',
                'start_date': datetime.now() + timedelta(days=14),
                'end_date': datetime.now() + timedelta(days=16),
                'location': 'Online',
                'event_type': 'Training',
                'attendees_count': 120,
                'is_virtual': True,
                'status': 'upcoming',
                'travel_emissions': 0.0,
                'venue_emissions': 0.0,
                'accommodation_emissions': 0.0,
                'catering_emissions': 0.0,
                'materials_emissions': 45.0,
                'digital_emissions': 180.0,
                'total_emissions': 225.0,
                'sustainability_score': 94,
                'sustainability_initiatives': json.dumps([
                    'Digital-only content',
                    'Optimized streaming settings',
                    'Low-bandwidth options for participants',
                    'Recording sessions to reduce repeat streams'
                ]),
                'carbon_offset_percentage': 100.0
            },
            {
                'name': 'Annual Team Retreat',
                'description': 'Our annual team retreat focusing on strategic planning and team bonding activities.',
                'start_date': datetime.now() - timedelta(days=45),
                'end_date': datetime.now() - timedelta(days=42),
                'location': 'Mountain View Resort',
                'event_type': 'Team-building',
                'attendees_count': 75,
                'is_virtual': False,
                'status': 'completed',
                'travel_emissions': 1250.0,
                'venue_emissions': 650.0,
                'accommodation_emissions': 1100.0,
                'catering_emissions': 525.0,
                'materials_emissions': 175.0,
                'digital_emissions': 50.0,
                'total_emissions': 3750.0,
                'sustainability_score': 61,
                'sustainability_initiatives': json.dumps([
                    'Eco-friendly venue selection',
                    'Carbon offset program',
                    'Sustainable transportation options',
                    'Waste reduction initiatives'
                ]),
                'carbon_offset_percentage': 35.0
            },
            {
                'name': 'Emissions Reduction Hackathon',
                'description': 'A two-day event where teams collaborate to develop innovative solutions for reducing company emissions.',
                'start_date': datetime.now() - timedelta(days=20),
                'end_date': datetime.now() - timedelta(days=19),
                'location': 'Company Innovation Center',
                'event_type': 'Workshop',
                'attendees_count': 60,
                'is_virtual': False,
                'status': 'completed',
                'travel_emissions': 350.0,
                'venue_emissions': 280.0,
                'accommodation_emissions': 200.0,
                'catering_emissions': 320.0,
                'materials_emissions': 120.0,
                'digital_emissions': 80.0,
                'total_emissions': 1350.0,
                'sustainability_score': 78,
                'sustainability_initiatives': json.dumps([
                    'Locally-sourced catering',
                    'Reusable materials only',
                    'Public transportation incentives',
                    'Digital collaboration tools to reduce paper'
                ]),
                'carbon_offset_percentage': 60.0
            },
            {
                'name': 'Executive Sustainability Summit',
                'description': 'A high-level meeting focusing on sustainability strategy and long-term environmental goals.',
                'start_date': datetime.now() - timedelta(days=90),
                'end_date': datetime.now() - timedelta(days=89),
                'location': 'Eco Business Center',
                'event_type': 'Conference',
                'attendees_count': 25,
                'is_virtual': False,
                'status': 'completed',
                'travel_emissions': 850.0,
                'venue_emissions': 150.0,
                'accommodation_emissions': 350.0,
                'catering_emissions': 125.0,
                'materials_emissions': 50.0,
                'digital_emissions': 30.0,
                'total_emissions': 1555.0,
                'sustainability_score': 72,
                'sustainability_initiatives': json.dumps([
                    'Green transportation options',
                    'Zero waste initiative',
                    'Energy-efficient venue',
                    'Sustainable gift packages'
                ]),
                'carbon_offset_percentage': 55.0
            }
        ]
        
        # Add all events to the database
        for event_data in events:
            event = CompanyEvent(**event_data)
            db.session.add(event)
        
        db.session.commit()

# Setup login manager loader
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
