# EcoPulse - Carbon Footprint Tracker

EcoPulse is a web application designed to help employees track and reduce their carbon footprint. The application provides personalized insights, recommendations, and progress tracking to encourage sustainable practices.

## Features

- **User Authentication**: Secure login and registration system
- **Carbon Footprint Tracking**: Track daily carbon emissions from commute, office, and travel
- **Personalized Goals**: Set and monitor monthly carbon reduction goals
- **Action Recommendations**: Get personalized suggestions to reduce carbon footprint
- **Progress Visualization**: Interactive charts and metrics to track progress
- **Activity Feed**: Monitor recent actions and achievements
- **Dark Theme Support**: Comfortable viewing experience in low-light conditions

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Migrations**: Alembic
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecopulse.git
cd ecopulse
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## Project Structure

```
ecopulse/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   └── api.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       └── employee/
│           └── dashboard.html
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── auth.js
│   │   └── dashboard.js
│   └── img/
│       └── ecopulse_logo.svg
├── migrations/
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── config.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 