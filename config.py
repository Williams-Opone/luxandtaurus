import os 
from flask import jsonify


SECRET_KEY = os.getenv('SECRET_KEY')

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_SERVER='smtp.gmail.com'

MAIL_PORT = 587

MAIL_USERNAME = os.getenv('MAIL_USERNAME')

MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

MAIL_USE_TLS = True

MAIL_USE_SSL = False



# This allows the login to work on your local computer (http vs https)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Get the directory where THIS config.py file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# The file you downloaded from Google Cloud
CLIENT_SECRETS_FILE =os.path.join(BASE_DIR, 'credentials.json')

# What we are asking Google for permission to do
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
