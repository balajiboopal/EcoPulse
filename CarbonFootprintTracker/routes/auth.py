"""
Authentication Routes

Handles user authentication, registration, and login/logout functionality.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from app import db
import logging

# Initialize blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Render the landing page."""
    try:
        if current_user.is_authenticated:
            if current_user.role == 'executive':
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('employee.dashboard'))
        return render_template('landing.html')
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}")
        return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Redirect based on role
            if user.role == 'executive':
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('employee.dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'employee')  # Default to employee
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
            
        # Create new user
        try:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logging.error(f"Error registering user: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration', 'error')
            
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
