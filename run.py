"""
run.py — Application entry point.

Run locally with:  python run.py
Deploy on Heroku/Render via:  gunicorn run:app
"""

import os
from app import create_app

# Select config based on FLASK_ENV environment variable
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
