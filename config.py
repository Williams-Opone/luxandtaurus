import os 
from flask import jsonify
SECRET_KEY = '89255d0f2a3859ded5b21e'

SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:@127.0.0.1:3306/luxandtaurus'

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_SERVER='smtp.gmail.com'

MAIL_PORT = 587

MAIL_USERNAME='williamsopone3@gmail.com'

MAIL_PASSWORD='ixzloikdmsrjydvh'

MAIL_USE_TLS = True

MAIL_USE_SSL = False

MAIL_DEFAULT_SENDER = 'williamsopone3@gmail.com'

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
