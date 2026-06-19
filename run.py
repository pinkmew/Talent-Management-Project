"""
run.py — Application entry point.

"""

import os
from app import create_app

# Select config based on FLASK_ENV environment variable
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
