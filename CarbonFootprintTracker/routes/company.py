"""
Company Routes

Handles routes for the company sustainability dashboard and executive views.
"""

import os
import stripe
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from carbon_calculator.calculator import CarbonFootprintCalculator
from ai_helpers.forecasting import CarbonForecaster
from models import User, CarbonFootprint, CompanyGoal, CompanyEvent
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta
import json
import logging

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Initialize blueprint
company_bp = Blueprint('company', __name__, url_prefix='/company')

# Initialize modules
calculator = CarbonFootprintCalculator()
forecaster = CarbonForecaster()

@company_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the company sustainability dashboard for executives."""
    # Check if user is an executive
    if current_user.role != 'executive':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('employee.dashboard'))
    
    # Get company-wide metrics
    metrics = get_company_metrics()
    
    # Get company goals
    goals = CompanyGoal.query.all()
    
    # Get department breakdown
    department_data = get_department_breakdown()
    
    # Get historical data for trends (last 6 months)
    trend_data = get_historical_trends()
    
    # Generate forecasts
    forecast_data = generate_company_forecast(metrics['current_month_data'])
    
    return render_template('company/dashboard.html',
                          user=current_user,
                          metrics=metrics,
                          goals=goals,
                          department_data=department_data,
                          trend_data=trend_data,
                          forecast_data=forecast_data)

def get_company_metrics():
    """Get overall company carbon metrics."""
    # Get current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    start_of_month = datetime(current_year, current_month, 1)
    
    # Get all footprints for current month
    current_footprints = CarbonFootprint.query.filter(
        CarbonFootprint.date >= start_of_month
    ).all()
    
    # Calculate total and average emissions
    total_emissions = sum(fp.total_footprint for fp in current_footprints) if current_footprints else 0
    avg_score = sum(fp.footprint_score for fp in current_footprints) / len(current_footprints) if current_footprints else 0
    
    # Get total employee count
    employee_count = User.query.filter_by(role='employee').count()
    
    # Get employees with footprint data
    employees_with_data = db.session.query(CarbonFootprint.user_id).distinct().count()
    
    # Calculate per-employee average
    per_employee = total_emissions / employees_with_data if employees_with_data > 0 else 0
    
    # Get previous month data for comparison
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    start_of_prev_month = datetime(prev_year, prev_month, 1)
    end_of_prev_month = start_of_month - timedelta(days=1)
    
    prev_footprints = CarbonFootprint.query.filter(
        CarbonFootprint.date >= start_of_prev_month,
        CarbonFootprint.date <= end_of_prev_month
    ).all()
    
    prev_total = sum(fp.total_footprint for fp in prev_footprints) if prev_footprints else 0
    
    # Calculate change percentage
    if prev_total > 0:
        change_percentage = ((total_emissions - prev_total) / prev_total) * 100
    else:
        change_percentage = 0
    
    # Prepare footprint data for forecasting
    footprint_data = []
    for fp in current_footprints:
        user = User.query.get(fp.user_id)
        if user:
            footprint_data.append({
                'user_id': fp.user_id,
                'total_footprint': fp.total_footprint,
                'footprint_score': fp.footprint_score
            })
    
    return {
        'total_emissions': round(total_emissions, 2),
        'avg_score': round(avg_score, 1),
        'employee_count': employee_count,
        'employees_with_data': employees_with_data,
        'per_employee': round(per_employee, 2),
        'change_percentage': round(change_percentage, 1),
        'change_direction': 'increase' if change_percentage > 0 else 'decrease',
        'current_month_data': footprint_data
    }

def get_department_breakdown():
    """
    Get carbon footprint breakdown by department.
    
    Note: This is a simplified version assuming all users are in a single department.
    In a real application, you would have department data in the User model.
    """
    # Simulate departments
    departments = ['Engineering', 'Marketing', 'Sales', 'Operations', 'HR']
    
    # Get all users with footprints
    users_with_footprints = db.session.query(CarbonFootprint.user_id).distinct().all()
    user_ids = [u[0] for u in users_with_footprints]
    
    # Assign users to random departments for this demo
    import random
    user_departments = {user_id: random.choice(departments) for user_id in user_ids}
    
    # Get latest footprint for each user
    latest_footprints = {}
    for user_id in user_ids:
        fp = CarbonFootprint.query.filter_by(user_id=user_id).order_by(CarbonFootprint.date.desc()).first()
        if fp:
            latest_footprints[user_id] = fp
    
    # Compile department data
    department_data = {}
    for dept in departments:
        department_data[dept] = {
            'count': 0,
            'total_emissions': 0,
            'avg_score': 0
        }
    
    # Aggregate data by department
    for user_id, footprint in latest_footprints.items():
        dept = user_departments.get(user_id, 'Other')
        department_data[dept]['count'] += 1
        department_data[dept]['total_emissions'] += footprint.total_footprint
        department_data[dept]['avg_score'] += footprint.footprint_score
    
    # Calculate averages
    for dept in department_data:
        if department_data[dept]['count'] > 0:
            department_data[dept]['avg_score'] = round(
                department_data[dept]['avg_score'] / department_data[dept]['count'], 1
            )
            department_data[dept]['avg_emissions'] = round(
                department_data[dept]['total_emissions'] / department_data[dept]['count'], 2
            )
    
    return department_data

def get_historical_trends():
    """Get historical carbon data trends for the past 6 months."""
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)  # Approximately 6 months
    
    # Get monthly aggregates
    monthly_data = []
    
    # Go through each month
    current_date = start_date
    while current_date <= end_date:
        month = current_date.month
        year = current_date.year
        
        # Get start and end of month
        start_of_month = datetime(year, month, 1).date()
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        end_of_month = datetime(next_year, next_month, 1).date() - timedelta(days=1)
        
        # If end_of_month is beyond our range, cap it
        if end_of_month > end_date:
            end_of_month = end_date
        
        # Query footprints for this month
        footprints = CarbonFootprint.query.filter(
            CarbonFootprint.date >= start_of_month,
            CarbonFootprint.date <= end_of_month
        ).all()
        
        # Calculate totals
        total_emissions = sum(fp.total_footprint for fp in footprints) if footprints else 0
        avg_score = sum(fp.footprint_score for fp in footprints) / len(footprints) if footprints else 0
        
        # Add to monthly data
        monthly_data.append({
            'month': start_of_month.strftime('%b %Y'),
            'emissions': round(total_emissions, 2),
            'score': round(avg_score, 1)
        })
        
        # Move to next month
        if month == 12:
            current_date = datetime(year + 1, 1, 1).date()
        else:
            current_date = datetime(year, month + 1, 1).date()
    
    return monthly_data

def generate_company_forecast(employee_data):
    """Generate company-wide carbon forecast."""
    # Use forecasting module to get projections
    forecast = forecaster.forecast_company_emissions(employee_data, months=12)
    
    # Prepare visualization-friendly data
    chart_data = {
        'labels': [],
        'baseline': [],
        'forecast': [],
        'savings': []
    }
    
    # Format data for charts
    for month_data in forecast['forecast']:
        month_name = f"{month_data['month']}/{month_data['year']}"
        chart_data['labels'].append(month_name)
        chart_data['baseline'].append(month_data['baseline'])
        chart_data['forecast'].append(month_data['emissions'])
        chart_data['savings'].append(month_data['savings'])
    
    # Add summary metrics
    annual_savings = forecast['total_annual_savings']
    percent_reduction = forecast['reduction_percentage']
    
    # Calculate equivalent impact metrics
    # Convert kg CO2 to meaningful equivalents
    trees_planted = round(annual_savings / 20)  # 20kg CO2 per tree per year (approximate)
    car_miles = round(annual_savings / 0.41 * 1000)  # 0.41kg CO2 per mile (from emission_factors)
    
    return {
        'chart_data': chart_data,
        'annual_savings': round(annual_savings, 2),
        'percent_reduction': percent_reduction,
        'employee_count': forecast['employee_count'],
        'avg_employee_emissions': forecast['average_employee_emissions'],
        'impact_equivalents': {
            'trees_planted': trees_planted,
            'car_miles': car_miles
        }
    }

@company_bp.route('/api/department_data')
@login_required
def api_department_data():
    """API endpoint to get department data for charts."""
    if current_user.role != 'executive':
        return jsonify({'error': 'Unauthorized'}), 403
    
    department_data = get_department_breakdown()
    return jsonify(department_data)

@company_bp.route('/api/trend_data')
@login_required
def api_trend_data():
    """API endpoint to get trend data for charts."""
    if current_user.role != 'executive':
        return jsonify({'error': 'Unauthorized'}), 403
    
    trend_data = get_historical_trends()
    return jsonify(trend_data)

@company_bp.route('/compliance')
@login_required
def compliance():
    """Render the compliance dashboard for executives."""
    # Check if user is an executive
    if current_user.role != 'executive':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('employee.dashboard'))
    
    from models import ComplianceStandard
    
    # Get compliance standards
    standards = ComplianceStandard.query.all()
    
    # If we don't have compliance standards in the database yet, we'll use the template's static data
    has_database_standards = len(standards) > 0
    
    return render_template('company/compliance.html',
                          user=current_user,
                          standards=standards,
                          has_database_standards=has_database_standards)

@company_bp.route('/api/compliance_data')
@login_required
def api_compliance_data():
    """API endpoint to get compliance data for charts and displays."""
    if current_user.role != 'executive':
        return jsonify({'error': 'Unauthorized'}), 403
    
    from models import ComplianceStandard
    
    # Get compliance standards
    standards = ComplianceStandard.query.all()
    
    # Format data for frontend
    standards_data = []
    for standard in standards:
        standards_data.append({
            'id': standard.id,
            'name': standard.name,
            'description': standard.description,
            'category': standard.category,
            'requirements': standard.requirements,
            'progress': standard.company_progress,
            'last_updated': standard.last_updated.strftime('%Y-%m-%d'),
            'icon': standard.icon,
            'status': 'Met' if standard.company_progress >= 80 else 'Action Needed'
        })
    
    return jsonify(standards_data)

@company_bp.route('/events')
@login_required
def events():
    """Render the company events page with carbon footprint tracking."""
    # Check if user is an executive
    if current_user.role != 'executive':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('employee.dashboard'))
    
    # Get upcoming and past events
    upcoming_events = CompanyEvent.query.filter(
        CompanyEvent.end_date >= datetime.now(),
        CompanyEvent.status != 'cancelled'
    ).order_by(CompanyEvent.start_date).all()
    
    past_events = CompanyEvent.query.filter(
        CompanyEvent.end_date < datetime.now()
    ).order_by(CompanyEvent.end_date.desc()).limit(10).all()
    
    # Get aggregate sustainability metrics
    total_events = CompanyEvent.query.count()
    total_emissions = db.session.query(func.sum(CompanyEvent.total_emissions)).scalar() or 0
    total_attendees = db.session.query(func.sum(CompanyEvent.attendees_count)).scalar() or 0
    
    # Create averages and other calculated metrics
    avg_emissions_per_event = total_emissions / total_events if total_events > 0 else 0
    avg_emissions_per_attendee = total_emissions / total_attendees if total_attendees > 0 else 0
    
    # Get carbon breakdown by event type
    events_by_type = db.session.query(
        CompanyEvent.event_type,
        func.sum(CompanyEvent.total_emissions).label('total_emissions'),
        func.count(CompanyEvent.id).label('count')
    ).group_by(CompanyEvent.event_type).all()
    
    event_type_data = {
        'labels': [],
        'emissions': [],
        'counts': []
    }
    
    for event_type, emissions, count in events_by_type:
        event_type_data['labels'].append(event_type)
        event_type_data['emissions'].append(round(emissions, 2))
        event_type_data['counts'].append(count)
    
    # Get emissions breakdown by source category
    emission_categories = [
        {'name': 'Travel', 'field': 'travel_emissions'},
        {'name': 'Venue', 'field': 'venue_emissions'},
        {'name': 'Accommodation', 'field': 'accommodation_emissions'},
        {'name': 'Catering', 'field': 'catering_emissions'},
        {'name': 'Materials', 'field': 'materials_emissions'},
        {'name': 'Digital', 'field': 'digital_emissions'}
    ]
    
    emissions_breakdown = {
        'labels': [cat['name'] for cat in emission_categories],
        'data': []
    }
    
    for category in emission_categories:
        field = category['field']
        total = db.session.query(func.sum(getattr(CompanyEvent, field))).scalar() or 0
        emissions_breakdown['data'].append(round(total, 2))
    
    # Calculate virtual vs in-person ratio
    virtual_events = CompanyEvent.query.filter_by(is_virtual=True).count()
    in_person_events = total_events - virtual_events
    
    virtual_vs_inperson = {
        'labels': ['Virtual', 'In-Person'],
        'counts': [virtual_events, in_person_events]
    }
    
    # Calculate trend data (emissions per quarter)
    quarters = []
    current_date = datetime.now().date()
    for i in range(4):  # Last 4 quarters
        quarter_start = current_date - timedelta(days=90 * (i + 1))
        quarter_end = current_date - timedelta(days=90 * i) if i > 0 else current_date
        
        quarter_total = db.session.query(func.sum(CompanyEvent.total_emissions)).filter(
            CompanyEvent.end_date >= quarter_start,
            CompanyEvent.end_date <= quarter_end
        ).scalar() or 0
        
        quarter_label = f"Q{((quarter_end.month-1)//3)+1} {quarter_end.year}"
        quarters.append({
            'label': quarter_label,
            'emissions': round(quarter_total, 2)
        })
    
    quarters.reverse()  # Show oldest first
    
    trend_data = {
        'labels': [q['label'] for q in quarters],
        'emissions': [q['emissions'] for q in quarters]
    }
    
    metrics = {
        'total_events': total_events,
        'total_emissions': round(total_emissions, 2),
        'total_attendees': total_attendees,
        'avg_emissions_per_event': round(avg_emissions_per_event, 2),
        'avg_emissions_per_attendee': round(avg_emissions_per_attendee, 2),
        'event_type_data': event_type_data,
        'emissions_breakdown': emissions_breakdown,
        'virtual_vs_inperson': virtual_vs_inperson,
        'trend_data': trend_data
    }
    
    return render_template('company/events.html',
                           user=current_user,
                           upcoming_events=upcoming_events,
                           past_events=past_events,
                           metrics=metrics)

@company_bp.route('/api/event/<int:event_id>')
@login_required
def api_event_detail(event_id):
    """API endpoint to get detailed event data."""
    if current_user.role != 'executive':
        return jsonify({'error': 'Unauthorized'}), 403
    
    event = CompanyEvent.query.get_or_404(event_id)
    
    # Create detailed emission breakdown for this event
    emissions_data = {
        'labels': ['Travel', 'Venue', 'Accommodation', 'Catering', 'Materials', 'Digital'],
        'data': [
            round(event.travel_emissions, 2),
            round(event.venue_emissions, 2),
            round(event.accommodation_emissions, 2),
            round(event.catering_emissions, 2),
            round(event.materials_emissions, 2),
            round(event.digital_emissions, 2)
        ]
    }
    
    # Format sustainability initiatives as array if present
    initiatives = []
    if event.sustainability_initiatives:
        try:
            initiatives = json.loads(event.sustainability_initiatives)
        except:
            initiatives = []
    
    # Calculate impact metrics
    co2_offset = event.total_emissions * (event.carbon_offset_percentage / 100)
    
    # Convert to meaningful equivalents
    trees_equivalent = round(event.total_emissions / 20)  # 20kg CO2 per tree per year (approximate)
    car_miles = round(event.total_emissions / 0.41 * 1000)  # 0.41kg CO2 per mile (from emission_factors)
    
    event_data = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'start_date': event.start_date.strftime('%Y-%m-%d %H:%M'),
        'end_date': event.end_date.strftime('%Y-%m-%d %H:%M'),
        'location': event.location,
        'event_type': event.event_type,
        'attendees_count': event.attendees_count,
        'is_virtual': event.is_virtual,
        'status': event.status,
        'total_emissions': round(event.total_emissions, 2),
        'emissions_breakdown': emissions_data,
        'sustainability_score': event.sustainability_score,
        'sustainability_initiatives': initiatives,
        'carbon_offset_percentage': event.carbon_offset_percentage,
        'co2_offset': round(co2_offset, 2),
        'impact_equivalents': {
            'trees_planted': trees_equivalent,
            'car_miles': car_miles
        }
    }
    
    return jsonify(event_data)

@company_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe checkout session for carbon offset donations."""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        return jsonify({'error': 'Please log in to make a donation'}), 401
    
    try:
        # Get amount and event_id from POST data
        data = request.json
        amount = data.get('amount', 1000)  # Amount in cents, default $10
        event_id = data.get('event_id')
        
        # Convert amount to integer safely
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            amount = 1000  # Default to $10 if conversion fails
        
        # Make sure we have a valid amount
        if amount < 100:  # Minimum $1.00
            amount = 100
        
        # Determine success and cancel URLs
        domain = request.host_url.rstrip('/')
        success_url = f"{domain}/company/donation-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{domain}/company/donation-cancel"
        
        # Create line item description
        description = "Carbon Offset Donation"
        if event_id:
            event = CompanyEvent.query.get(event_id)
            if event:
                description = f"Carbon Offset for: {event.name}"
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Carbon Offset Donation',
                        'description': description,
                        'images': ['https://images.unsplash.com/photo-1464822759023-fed622ff2c3b']
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'event_id': event_id if event_id else '',
                'user_id': current_user.id
            }
        )
        
        # Return the session ID and public key for the frontend to redirect
        return jsonify({
            'id': checkout_session.id,
            'publicKey': os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_placeholder')
        })
    
    except Exception as e:
        logging.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@company_bp.route('/donation-success')
@login_required
def donation_success():
    """Handle successful donations."""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid donation session.', 'error')
        return redirect(url_for('company.events'))
    
    try:
        # Retrieve session data from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Get event ID from metadata
        event_id = checkout_session.metadata.get('event_id')
        
        # Update the event's carbon offset amount if applicable
        if event_id and event_id.isdigit():
            event = CompanyEvent.query.get(int(event_id))
            if event and hasattr(checkout_session, 'payment_intent') and checkout_session.payment_intent:
                # Get payment amount
                payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)
                if payment_intent:
                    donation_amount = payment_intent.amount / 100  # Convert cents to dollars
                    
                    # Calculate additional offset percentage (simple calculation for demo)
                    # Assuming $1 = 10kg CO2 offset for demonstration
                    additional_offset_kg = donation_amount * 10
                    
                    # Update event record
                    event.carbon_offset_percentage += min(5, (additional_offset_kg / event.total_emissions) * 100)
                    if event.carbon_offset_percentage > 100:
                        event.carbon_offset_percentage = 100
                    
                    db.session.commit()
        
        # Calculate impact statistics for the donation
        donation_stats = None
        try:
            # Get payment amount
            payment_intent = None
            donation_amount = 0
            
            # Get the payment intent from checkout session
            if hasattr(checkout_session, 'payment_intent') and checkout_session.payment_intent:
                payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)
                if payment_intent:
                    donation_amount = payment_intent.amount / 100  # Convert cents to dollars
                
            # Calculate environmental impact
            # These are simplified calculations for demonstration purposes
            carbon_offset_kg = donation_amount * 10  # Assume $1 = 10kg CO2 offset
            trees_planted = int(donation_amount * 0.5)  # Assume $2 = 1 tree
            car_miles = int(carbon_offset_kg * 2.5)  # Assume 1kg CO2 = 2.5 miles of driving
            
            donation_stats = {
                'amount': donation_amount,
                'carbon_offset_kg': carbon_offset_kg,
                'trees_planted': trees_planted,
                'car_miles': car_miles
            }
        except Exception as e:
            logging.error(f"Error calculating donation stats: {str(e)}")
        
        # Don't redirect to events page, show the success page instead
        return render_template('company/success.html', 
                               session_id=session_id, 
                               event_id=event_id,
                               donation_stats=donation_stats)
        
    except Exception as e:
        logging.error(f"Error processing donation success: {str(e)}")
        flash('There was an error processing your donation. Please contact support.', 'error')
        return redirect(url_for('company.events'))

@company_bp.route('/donation-cancel')
def donation_cancel():
    """Handle cancelled donations."""
    return render_template('company/cancel.html')
