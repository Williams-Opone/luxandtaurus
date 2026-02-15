from flask  import Flask,session,jsonify
from flask_mail import Mail,Message
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


db= SQLAlchemy()

mail=Mail()
csrf = CSRFProtect()
def create_app():
    app = Flask(__name__)
    
    app.config.from_pyfile('config.py',silent=True)
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate = Migrate(app,db)
    
    return app

app = create_app()

def get_gmail_service():
    """Rebuilds the connection to Gmail using the saved token."""
    if 'credentials' not in session:
        return None
    
    creds_data = session['credentials']
    creds = Credentials(**creds_data)
    
    return build('gmail', 'v1', credentials=creds)

def fetch_real_emails():
    """The function that actually goes to Google and gets your emails."""
    service = get_gmail_service()
    if not service:
        return []

    try:
        # 1. Ask for the last 10 messages in Inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
        messages = results.get('messages', [])
        
        email_data = []
        
        # 2. Loop through them and get details (Subject, Sender, Snippet)
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = txt['payload']['headers']
            
            # Helper to find header values
            def get_header(name):
                for h in headers:
                    if h['name'] == name:
                        return h['value']
                return ""

            email_data.append({
                "id": msg['id'],
                "sender": get_header("From").split('<')[0].replace('"', ''), 
                "email": get_header("From"),
                "subject": get_header("Subject"),
                "preview": txt.get('snippet', ''),
                "body": txt.get('snippet', ''), 
                "date": get_header("Date")[:16], 
                "status": "new" if 'UNREAD' in txt['labelIds'] else "read",
                "avatar": get_header("From")[0].upper() if get_header("From") else "U"
            })
            
        return email_data
        
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []



from project import config,model, userroute,adminroute