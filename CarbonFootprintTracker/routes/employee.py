"""
Employee Routes

Handles routes for the employee dashboard and carbon footprint tracking.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from sqlalchemy import func
from carbon_calculator.calculator import CarbonFootprintCalculator
from ai_helpers.recommendations import RecommendationEngine
from ai_helpers.forecasting import CarbonForecaster
from ai_helpers.quiz import SustainabilityQuiz
from models import User, CarbonFootprint, TrainingProgress, SustainabilityTip, TransactionData, QuizScore
from app import db
from datetime import datetime, timedelta
import json
import logging

# Initialize blueprint
employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

# Initialize modules
calculator = CarbonFootprintCalculator()
recommendation_engine = RecommendationEngine()
forecaster = CarbonForecaster()
quiz = SustainabilityQuiz()

@employee_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the employee dashboard."""
    # Get the user's most recent carbon footprint
    latest_footprint = CarbonFootprint.query.filter_by(user_id=current_user.id).order_by(CarbonFootprint.date.desc()).first()
    
    # Get historical footprints for charts (last 6 entries)
    footprint_history = CarbonFootprint.query.filter_by(user_id=current_user.id).order_by(CarbonFootprint.date.desc()).limit(6).all()
    footprint_history = list(reversed(footprint_history))  # Reverse to get chronological order
    
    # Format data for charts
    dates = [fp.date.strftime('%m/%d') for fp in footprint_history]
    scores = [fp.footprint_score for fp in footprint_history]
    emissions = [fp.total_footprint for fp in footprint_history]
    
    # Get personalized recommendations if we have footprint data
    recommendations = []
    if latest_footprint:
        # Prepare user data for recommendation engine - handle old and new model fields
        try:
            user_data = {
                'commute_distance': latest_footprint.commute_distance or 0,
                'car_type': latest_footprint.car_type or 'gas', 
            }
            
            # Add new model fields if they exist
            if hasattr(latest_footprint, 'commute_days_by_car'):
                user_data['commute_days_by_car'] = latest_footprint.commute_days_by_car or 0
            if hasattr(latest_footprint, 'commute_days_public_transit'):
                user_data['commute_days_public_transit'] = latest_footprint.commute_days_public_transit or 0
            if hasattr(latest_footprint, 'commute_days_ev'):
                user_data['commute_days_ev'] = latest_footprint.commute_days_ev or 0
            if hasattr(latest_footprint, 'remote_work_days'):
                user_data['remote_work_days'] = latest_footprint.remote_work_days or 0
            if hasattr(latest_footprint, 'video_conference_hours'):
                user_data['video_conference_hours'] = latest_footprint.video_conference_hours or 0
            if hasattr(latest_footprint, 'air_travel_miles'):
                user_data['air_travel_miles'] = latest_footprint.air_travel_miles or 0
            if hasattr(latest_footprint, 'hotel_nights'):
                user_data['hotel_nights'] = latest_footprint.hotel_nights or 0
            if hasattr(latest_footprint, 'computer_hours'):
                user_data['computer_hours'] = latest_footprint.computer_hours or 0
            if hasattr(latest_footprint, 'printer_pages'):
                user_data['printer_pages'] = latest_footprint.printer_pages or 0
            if hasattr(latest_footprint, 'hvac_usage'):
                user_data['hvac_usage'] = latest_footprint.hvac_usage or 'medium'
            if hasattr(latest_footprint, 'has_transaction_data'):
                user_data['has_transaction_data'] = latest_footprint.has_transaction_data or False
            
            # For backward compatibility
            if hasattr(latest_footprint, 'diet_type'):
                user_data['diet_type'] = latest_footprint.diet_type
            if hasattr(latest_footprint, 'local_food_percentage'):
                user_data['local_food_percentage'] = latest_footprint.local_food_percentage
            if hasattr(latest_footprint, 'office_days_per_week'):
                user_data['office_days_per_week'] = latest_footprint.office_days_per_week
            if hasattr(latest_footprint, 'paper_usage'):
                user_data['paper_usage'] = latest_footprint.paper_usage
            if hasattr(latest_footprint, 'energy_usage'):
                user_data['energy_usage'] = latest_footprint.energy_usage
            
            recommendations = recommendation_engine.get_personalized_recommendations(user_data, limit=3)
        except Exception as e:
            logging.error(f"Error generating recommendations: {str(e)}")
            recommendations = []
    
    # Get latest quiz score
    latest_quiz = QuizScore.query.filter_by(user_id=current_user.id).order_by(QuizScore.quiz_date.desc()).first()
    
    # Get forecast data if we have footprint data
    forecast_data = None
    if latest_footprint:
        forecast_data = forecaster.forecast_individual_emissions(latest_footprint.total_footprint, months=6)
    
    return render_template('employee/dashboard.html', 
                          user=current_user,
                          latest_footprint=latest_footprint,
                          dates=json.dumps(dates),
                          scores=json.dumps(scores),
                          emissions=json.dumps(emissions),
                          recommendations=recommendations,
                          latest_quiz=latest_quiz,
                          forecast_data=forecast_data)

@employee_bp.route('/carbon_form', methods=['GET', 'POST'])
@login_required
def carbon_form():
    """Handle carbon footprint form submission for both office and personal spending."""
    if request.method == 'POST':
        try:
            form_type = request.form.get('form_type', 'office')
            transaction_footprint = 0.0
            has_transaction_data = False
            
            if form_type == 'office':
                # Get form data for commute
                commute_distance = float(request.form.get('commute_distance', 0))
                car_type = request.form.get('car_type')
                commute_days_by_car = int(request.form.get('commute_days_by_car', 0))
                commute_days_public_transit = int(request.form.get('commute_days_public_transit', 0))
                commute_days_ev = int(request.form.get('commute_days_ev', 0))
                
                # Get remote work data
                remote_work_days = int(request.form.get('remote_work_days', 0))
                video_conference_hours = float(request.form.get('video_conference_hours', 0))
                
                # Get business travel data
                air_travel_miles = float(request.form.get('air_travel_miles', 0))
                hotel_nights = int(request.form.get('hotel_nights', 0))
                rental_car_days = int(request.form.get('rental_car_days', 0))
                
                # Get office equipment usage
                computer_hours = float(request.form.get('computer_hours', 0))
                printer_pages = int(request.form.get('printer_pages', 0))
                hvac_usage = request.form.get('hvac_usage', 'medium')
                
                # Calculate carbon footprint components
                commute_data = {
                    'distance': commute_distance,
                    'days_by_car': commute_days_by_car,
                    'days_public_transit': commute_days_public_transit,
                    'days_ev': commute_days_ev,
                    'car_type': car_type
                }
                
                office_data = {
                    'remote_days': remote_work_days,
                    'video_hours': video_conference_hours,
                    'computer_hours': computer_hours,
                    'printer_pages': printer_pages,
                    'hvac_usage': hvac_usage
                }
                
                travel_data = {
                    'air_miles': air_travel_miles,
                    'hotel_nights': hotel_nights,
                    'rental_car_days': rental_car_days
                }
                
                # Calculate total footprint from components
                commute_footprint = calculator.calculate_commute_footprint(commute_data)
                office_footprint = calculator.calculate_office_footprint(office_data)
                travel_footprint = calculator.calculate_travel_footprint(travel_data)
                total_footprint = commute_footprint + office_footprint + travel_footprint
                
                flash_message = 'Your office carbon footprint has been calculated and saved!'
            
            elif form_type == 'personal':
                # For personal spending, we'll process transaction data
                has_transaction_data = True
                transaction_data_period = 'month'  # Default to monthly
                
                # In a real application, we would process actual transactions from payment providers
                # For this demo, we'll use a fixed value
                transaction_footprint = 15.8  # kg CO2
                commute_footprint = 0
                office_footprint = 0
                travel_footprint = 0
                total_footprint = transaction_footprint
                
                # Save transaction data if submitted
                if 'merchant' in request.form and request.form.get('merchant') and 'amount' in request.form and request.form.get('amount'):
                    try:
                        transaction = TransactionData(
                            user_id=current_user.id,
                            transaction_date=datetime.now(),
                            category=request.form.get('category', 'other'),
                            merchant=request.form.get('merchant'),
                            amount=float(request.form.get('amount', 0)),
                            carbon_impact=float(request.form.get('amount', 0)) * 0.1,  # Simple estimation
                            description=request.form.get('description', ''),
                            source='manual'
                        )
                        db.session.add(transaction)
                        db.session.commit()
                    except Exception as e:
                        logging.error(f"Error saving transaction data: {str(e)}")
                        # Continue with the rest of the function even if transaction saving fails
                
                flash_message = 'Your personal spending carbon footprint has been calculated and saved!'
                
                # These values aren't relevant for personal spending but are needed for the model
                commute_distance = 0
                car_type = "gas"
                commute_days_by_car = 0
                commute_days_public_transit = 0
                commute_days_ev = 0
                remote_work_days = 0
                video_conference_hours = 0
                air_travel_miles = 0
                hotel_nights = 0
                rental_car_days = 0
                computer_hours = 0
                printer_pages = 0
                hvac_usage = 'medium'
            
            # Calculate footprint score (0-100, lower is better)
            footprint_score = calculator.calculate_footprint_score(total_footprint)
            
            # Save to database with the new model fields
            footprint = CarbonFootprint(
                user_id=current_user.id,
                date=datetime.now().date(),
                
                # Commute data
                commute_distance=commute_distance,
                car_type=car_type,
                commute_days_by_car=commute_days_by_car,
                commute_days_public_transit=commute_days_public_transit,
                commute_days_ev=commute_days_ev,
                
                # Remote work
                remote_work_days=remote_work_days,
                video_conference_hours=video_conference_hours,
                
                # Business travel
                air_travel_miles=air_travel_miles,
                hotel_nights=hotel_nights,
                rental_car_days=rental_car_days,
                
                # Office equipment
                computer_hours=computer_hours,
                printer_pages=printer_pages,
                hvac_usage=hvac_usage,
                
                # Transaction data
                has_transaction_data=has_transaction_data,
                transaction_data_period='month' if has_transaction_data else None,
                transaction_footprint=transaction_footprint,
                
                # Calculated values
                commute_footprint=commute_footprint,
                office_footprint=office_footprint,
                travel_footprint=travel_footprint,
                total_footprint=total_footprint,
                footprint_score=footprint_score,
                
                # For backward compatibility
                diet_type="mixed",
                local_food_percentage=50
            )
            
            db.session.add(footprint)
            db.session.commit()
            
            flash(flash_message, 'success')
            return redirect(url_for('employee.dashboard'))
            
        except Exception as e:
            logging.error(f"Error calculating carbon footprint: {str(e)}")
            flash('An error occurred while calculating your carbon footprint.', 'error')
    
    # For GET request, render the form with current date for transaction form
    return render_template('employee/carbon_form.html', current_date=datetime.now().strftime('%Y-%m-%d'))

@employee_bp.route('/transactions', methods=['POST'])
@login_required
def add_transaction():
    """Add a manual transaction for carbon footprint tracking."""
    try:
        # Get transaction data from form
        transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d')
        merchant = request.form.get('merchant')
        category = request.form.get('category')
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description', '')
        
        # Simple carbon impact calculation based on category and amount
        # In a real application, this would be more sophisticated
        carbon_factors = {
            'food': 0.4,         # kg CO2 per dollar
            'groceries': 0.2,    # kg CO2 per dollar
            'transportation': 0.5, # kg CO2 per dollar
            'shopping': 0.3,     # kg CO2 per dollar
            'utilities': 0.6,    # kg CO2 per dollar
            'travel': 0.8,       # kg CO2 per dollar
            'entertainment': 0.2  # kg CO2 per dollar
        }
        
        carbon_impact = amount * carbon_factors.get(category, 0.3)  # Default factor if category not found
        
        # Create and save transaction
        transaction = TransactionData(
            user_id=current_user.id,
            transaction_date=transaction_date,
            category=category,
            merchant=merchant,
            amount=amount,
            carbon_impact=carbon_impact,
            description=description,
            source='manual'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'transaction': {
                'merchant': merchant,
                'category': category,
                'amount': amount,
                'carbon_impact': round(carbon_impact, 2)
            }
        })
        
    except Exception as e:
        logging.error(f"Error adding transaction: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@employee_bp.route('/training')
@login_required
def training():
    """Render the sustainability training dashboard."""
    # Get user's training progress
    user_training = TrainingProgress.query.filter_by(user_id=current_user.id).all()
    
    # If no training data exists, initialize with default modules
    if not user_training:
        default_modules = [
            {"id": 1, "name": "Introduction to Carbon Management", "description": "Learn the basics of carbon footprints and how they are calculated."},
            {"id": 2, "name": "Sustainable Transportation", "description": "Discover strategies to reduce transportation emissions."},
            {"id": 3, "name": "Energy Efficiency in the Workplace", "description": "Learn how to minimize energy usage at work."},
            {"id": 4, "name": "Remote Work and Sustainability", "description": "Understand the environmental impact of remote work."},
            {"id": 5, "name": "Business Travel Best Practices", "description": "Learn how to reduce the carbon impact of necessary business travel."}
        ]
        
        for module in default_modules:
            progress = TrainingProgress(
                user_id=current_user.id,
                module_id=module["id"],
                module_name=module["name"],
                completion_percentage=0.0,
                completed=False
            )
            db.session.add(progress)
        
        db.session.commit()
        user_training = TrainingProgress.query.filter_by(user_id=current_user.id).all()
    
    # Calculate overall progress
    total_modules = len(user_training)
    completed_modules = sum(1 for module in user_training if module.completed)
    overall_progress = int((sum(module.completion_percentage for module in user_training) / total_modules) if total_modules > 0 else 0)
    
    # Get certificates issued
    certificates = [module for module in user_training if module.certificate_issued]
    
    return render_template('employee/training.html', 
                          user=current_user,
                          modules=user_training,
                          overall_progress=overall_progress,
                          completed_modules=completed_modules,
                          total_modules=total_modules,
                          certificates=certificates)

@employee_bp.route('/training/<int:module_id>')
@login_required
def view_training_module(module_id):
    """View a specific training module."""
    # Get the training module progress
    module = TrainingProgress.query.filter_by(user_id=current_user.id, module_id=module_id).first_or_404()
    
    # Placeholder for module content - in a real app, this would come from a CMS or database
    module_content = {
        1: {"title": "Introduction to Carbon Management", "sections": 5, "current_section": int(module.completion_percentage / 20) + 1},
        2: {"title": "Sustainable Transportation", "sections": 4, "current_section": int(module.completion_percentage / 25) + 1},
        3: {"title": "Energy Efficiency in the Workplace", "sections": 6, "current_section": int(module.completion_percentage / 16.66) + 1},
        4: {"title": "Remote Work and Sustainability", "sections": 4, "current_section": int(module.completion_percentage / 25) + 1},
        5: {"title": "Business Travel Best Practices", "sections": 5, "current_section": int(module.completion_percentage / 20) + 1}
    }
    
    content = module_content.get(module_id, {"title": module.module_name, "sections": 5, "current_section": 1})
    
    return render_template('employee/training_module.html',
                          module=module,
                          content=content,
                          user=current_user)

@employee_bp.route('/training/update_progress', methods=['POST'])
@login_required
def update_training_progress():
    """Update training module progress."""
    if request.method == 'POST':
        module_id = request.form.get('module_id', type=int)
        progress = request.form.get('progress', type=float)
        completed = request.form.get('completed', type=bool, default=False)
        
        if not module_id or progress is None:
            flash('Invalid request parameters', 'error')
            return redirect(url_for('employee.training'))
        
        module = TrainingProgress.query.filter_by(user_id=current_user.id, module_id=module_id).first()
        
        if not module:
            flash('Module not found', 'error')
            return redirect(url_for('employee.training'))
        
        # Update progress
        module.completion_percentage = progress
        module.completed = completed
        module.last_activity = datetime.now()
        
        # If completed, maybe issue a certificate
        if completed and progress >= 100 and not module.certificate_issued:
            module.certificate_issued = True
        
        db.session.commit()
        
        flash('Training progress updated', 'success')
        
        return redirect(url_for('employee.view_training_module', module_id=module_id))
    
    return redirect(url_for('employee.training'))

@employee_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def take_quiz():
    """Take a sustainability quiz."""
    # Generate a new quiz with 10 questions
    questions_with_answers = quiz.generate_quiz(num_questions=10)
    
    if request.method == 'POST':
        # Get the quiz key from session
        session_key = session.get('current_quiz_key')
        if not session_key:
            flash('Quiz session expired. Please start a new quiz.', 'warning')
            return redirect(url_for('employee.take_quiz'))
            
        # Get questions JSON using the session key
        questions_json = session.get(session_key, '')
        if not questions_json:
            flash('Quiz data not found. Please start a new quiz.', 'warning')
            return redirect(url_for('employee.take_quiz'))
            
        # Deserialize questions from JSON
        try:
            questions_with_answers = json.loads(questions_json)
            # Clean up session after use
            session.pop(session_key, None)
            session.pop('current_quiz_key', None)
        except json.JSONDecodeError:
            flash('Error loading quiz data. Please start a new quiz.', 'warning')
            return redirect(url_for('employee.take_quiz'))
            
        # Handle quiz submission
        user_answers = []
        score = 0
        total_possible = len(questions_with_answers)
        results = []
        
        for q in questions_with_answers:
            answer_key = f"question_{q['id']}"
            selected_answer = request.form.get(answer_key)
            
            if selected_answer:
                # Convert to integer as the form value comes as a string
                selected_idx = int(selected_answer)
                user_answers.append({
                    'question_id': q['id'],
                    'selected_answer': selected_idx
                })
                
                # Check if the answer is correct
                is_correct = (selected_idx == q['correct_answer'])
                if is_correct:
                    score += 1
                
                # Add detailed result for display
                results.append({
                    'question_text': q['question'],
                    'selected_answer': q['options'][selected_idx],
                    'correct_text': q['options'][q['correct_answer']],
                    'correct': is_correct,
                    'explanation': q['explanation']
                })
        
        # Calculate percentage
        percentage = (score / total_possible) * 100 if total_possible > 0 else 0
        
        # Save quiz score to database
        quiz_score = QuizScore(
            user_id=current_user.id,
            score=score,
            total_possible=total_possible,
            percentage=percentage,
            quiz_date=datetime.now()
        )
        
        db.session.add(quiz_score)
        db.session.commit()
        
        # Prepare results for display
        quiz_results = {
            'score': score,
            'total': total_possible,
            'percentage': percentage,
            'results': results
        }
        
        flash(f'Quiz completed! Your score: {score}/{total_possible} ({percentage:.1f}%)', 'success')
        
        # Return the results page with detailed feedback
        return render_template('employee/quiz.html', 
                              completed=True, 
                              results=quiz_results, 
                              user=current_user)
    
    # For GET request, prepare the quiz questions by removing answers
    display_questions = []
    for q in questions_with_answers:
        question_copy = q.copy()
        # Remove the answer and explanation for frontend display
        question_copy.pop('correct_answer', None)
        question_copy.pop('explanation', None)
        display_questions.append(question_copy)
    
    # Store the full questions with answers in session for validation on POST
    # Use a unique session key for each quiz to prevent conflicts
    session_key = f'quiz_{datetime.now().timestamp()}'
    session['current_quiz_key'] = session_key
    session[session_key] = json.dumps(questions_with_answers)
    
    # For GET request, render the quiz form
    return render_template('employee/quiz.html', 
                          completed=False, 
                          questions=display_questions, 
                          user=current_user)

@employee_bp.route('/peer_comparison')
@login_required
def peer_comparison():
    """Render the peer comparison dashboard."""
    # Get the user's latest carbon footprint
    latest_footprint = CarbonFootprint.query.filter_by(user_id=current_user.id).order_by(CarbonFootprint.date.desc()).first()
    
    if not latest_footprint:
        flash('Please submit your carbon footprint data first.', 'info')
        return redirect(url_for('employee.carbon_form'))
    
    # Get company and department averages
    company_avg = db.session.query(
        func.avg(CarbonFootprint.total_footprint).label('avg_footprint'),
        func.avg(CarbonFootprint.footprint_score).label('avg_score')
    ).first()
    
    # Get department average if user has a department
    dept_avg = None
    if current_user.department:
        # Get all users in the department
        dept_users = User.query.filter_by(department=current_user.department).all()
        dept_user_ids = [user.id for user in dept_users]
        
        # Get average footprint for department members
        dept_avg = db.session.query(
            func.avg(CarbonFootprint.total_footprint).label('avg_footprint'),
            func.avg(CarbonFootprint.footprint_score).label('avg_score')
        ).filter(CarbonFootprint.user_id.in_(dept_user_ids)).first()
    
    # Get top performers in company and department
    top_company = CarbonFootprint.query.order_by(CarbonFootprint.footprint_score.desc()).limit(5).all()
    
    # Get department leaderboard if user has a department
    top_department = []
    if current_user.department:
        top_department = CarbonFootprint.query.join(User).filter(
            User.department == current_user.department
        ).order_by(CarbonFootprint.footprint_score.desc()).limit(5).all()
    
    # Get user's percentile
    # This is simplified - in a real app you'd need more complex calculation
    better_than_count = CarbonFootprint.query.filter(
        CarbonFootprint.footprint_score < latest_footprint.footprint_score
    ).count()
    total_users = CarbonFootprint.query.distinct(CarbonFootprint.user_id).count()
    percentile = int((better_than_count / total_users * 100) if total_users > 0 else 0)
    
    return render_template('employee/peer_comparison.html',
                          user=current_user,
                          latest_footprint=latest_footprint,
                          company_avg=company_avg,
                          dept_avg=dept_avg,
                          top_company=top_company,
                          top_department=top_department,
                          percentile=percentile)

@employee_bp.route('/api/forecast')
@login_required
def get_forecast_data():
    """API endpoint to get forecast data for charts."""
    # Get the user's most recent carbon footprint
    latest_footprint = CarbonFootprint.query.filter_by(user_id=current_user.id).order_by(CarbonFootprint.date.desc()).first()
    
    if not latest_footprint:
        return jsonify({'error': 'No carbon footprint data available'}), 404
    
    # Generate forecast data
    forecast_data = forecaster.forecast_individual_emissions(latest_footprint.total_footprint, months=12)
    
    return jsonify(forecast_data)
