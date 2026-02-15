import os
import secrets
import base64
from email.mime.text import MIMEText
from flask import render_template, request, flash, session, redirect, url_for, jsonify,current_app
from flask_mail import Message

# Google Auth
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from project import app, mail, csrf,fetch_real_emails,db
from .model import Admin,Project,Contact




def get_gmail_service():
    """Rebuilds the connection to Gmail using the saved token from session."""
    if 'credentials' not in session:
        return None
    
    creds_data = session['credentials']
    creds = Credentials(**creds_data)
    
    return build('gmail', 'v1', credentials=creds)

def search_gmail(query=None, page_token=None, label_ids=None):
    """Fetches a limited set of emails with specific metadata."""
    service = get_gmail_service()
    if not service:
        return {'emails': [], 'nextPageToken': None}

    # Default to INBOX if no label is provided
    if label_ids is None:
        label_ids = ['INBOX']

    try:
        # Requesting exactly 7 results to fit your dashboard layout
        results = service.users().messages().list(
            userId='me', 
            labelIds=label_ids, 
            maxResults=7, 
            q=query, 
            pageToken=page_token
        ).execute()
        
        messages = results.get('messages', [])
        next_token = results.get('nextPageToken', None)
        email_data = []
        
        for msg in messages:
            # Fetch full message details
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = txt['payload']['headers']
            
            def get_header(name):
                for h in headers:
                    if h['name'] == name:
                        return h['value']
                return ""

            raw_sender = get_header("From")
            sender_name = raw_sender.split('<')[0].replace('"', '').strip() if raw_sender else "Unknown"

            email_data.append({
                "id": msg['id'],
                "sender": sender_name, 
                "email": raw_sender, 
                "subject": get_header("Subject"),
                "preview": txt.get('snippet', ''),
                "body": txt.get('snippet', ''), 
                "date": get_header("Date")[:16], 
                "status": "new" if 'UNREAD' in txt['labelIds'] else "read"
            })
            
        return {'emails': email_data, 'nextPageToken': next_token}
        
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return {'emails': [], 'nextPageToken': None}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_input = request.form.get('email')
        password_input = request.form.get('password')

        admin = Admin.query.filter_by(email=email_input).first()

        if admin and admin.check_password(password_input):
            # --- THIS IS THE MISSING PIECE ---
            session['logged_in'] = True 
            session['user_email'] = admin.email  # <--- ADD THIS LINE HERE
            # ---------------------------------
            
            flash("Login Successful", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return render_template('admin/adminsignin.html')
            
    return render_template('admin/adminsignin.html')

@app.route("/admin/dashboard")
def admin_dashboard():
    # 0. Security & Personalization Logic
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get the email from the session (saved during login)
    current_email = session.get('user_email')
    
    # Query the Database for this specific Admin
    current_admin = Admin.query.filter_by(email=current_email).first()
    
    # Extract the name (or default to "Admin" if something goes wrong)
    display_name = current_admin.name if current_admin else "Admin"

    # 1. Get High-Level Stats
    total_projects = Project.query.count()
    total_messages = Contact.query.count()
    
    # 2. Get Recent Data for the "Feed"
    recent_contacts = Contact.query.order_by(Contact.date_sent.desc()).limit(5).all()
    recent_projects = Project.query.order_by(Project.date_posted.desc()).limit(3).all()
    unread_count = Contact.query.filter_by(status='New').count()
    return render_template('admin/dashboard.html', 
                           total_projects=total_projects, 
                           total_messages=total_messages,
                           recent_contacts=recent_contacts,
                           recent_projects=recent_projects,
                           admin_name=display_name,unread_count=unread_count) # <--- Pass the name here


# 1. The "Trigger" Route - Sends you to Google
@app.route('/admin/connect-gmail')
def connect_gmail():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    flow = Flow.from_client_secrets_file(
        current_app.config['CLIENT_SECRETS_FILE'],
        scopes=current_app.config['SCOPES'],
        redirect_uri=url_for('gmail_callback', _external=True) 
    )
    
    # THE FIX IS HERE: Add prompt='select_account' and 'consent'
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account consent' # This forces the account selector to appear
    )
    
    session['state'] = state
    return redirect(authorization_url)

# 2. The "Callback" Route - Google sends you back here
@app.route('/admin/callback')
def gmail_callback():
    state = session['state']
    
    flow = Flow.from_client_secrets_file(
        current_app.config['CLIENT_SECRETS_FILE'],
        scopes=current_app.config['SCOPES'],
        state=state,
        redirect_uri=url_for('gmail_callback', _external=True)
    )
    
    # Exchange the code Google gave us for an actual Token
    flow.fetch_token(authorization_response=request.url)

    # Save the credentials in the session (THIS FIXES YOUR ISSUE)
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect(url_for('admin_inquiries'))

@app.route('/admin/inquiries')
def admin_inquiries():
    unread_count = Contact.query.filter_by(status='New').count()
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get the page token to maintain pagination state
    page_token = request.args.get('page_token')
    display_name = session.get('admin_name', 'Admin')

    # Fetching database leads (Internal CRM)
    db_inquiries = Contact.query.order_by(Contact.date_sent.desc()).all()

    try:
        # Fetching Gmail leads (External Inbox)
        gmail_data = search_gmail(page_token=page_token) 
        gmail_inquiries = gmail_data.get('emails', [])
        next_page_token = gmail_data.get('nextPageToken')
        
    except Exception as e:
        print(f"Gmail Sync Error: {e}")
        # If the token is dead, we need to re-authenticate
        return redirect(url_for('connect_gmail'))

    return render_template('admin/inquiries.html', 
                           inquiries=db_inquiries, 
                           gmails=gmail_inquiries,
                           next_page=next_page_token,
                           admin_name=display_name,unread_count=unread_count)

@app.route('/admin/update_inquiry/<int:inquiry_id>', methods=['POST'])
def update_inquiry(inquiry_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    inquiry = Contact.query.get_or_404(inquiry_id)
    
    # Capture current page_token so the redirect doesn't reset the view
    page_token = request.args.get('page_token')

    try:
        # Update the Internal Admin Fields from the form
        inquiry.status = request.form.get('status')
        inquiry.notes = request.form.get('notes')
        
        db.session.commit()
        flash(f"Protocol updated for {inquiry.name}.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Database Write Error: {e}")
        flash("Update failed. Check system logs.", "danger")

    # Return to dashboard, preserving the Gmail page if it was provided
    return redirect(url_for('admin_inquiries', page_token=page_token))





@app.route("/admin/upload-project", methods=['GET', 'POST'])
def upload_project():
    if request.method == 'POST':
        action = request.form.get('action')

        # --- DELETE ACTION ---
        if action == 'delete':
            project_id = request.form.get('project_id')
            project = Project.query.get_or_404(project_id)
            db.session.delete(project)
            db.session.commit()
            flash('Project deleted successfully.', 'success')
            return redirect(url_for('upload_project'))

        # --- UPLOAD OR UPDATE ACTION ---
        title = request.form.get('title')
        category = request.form.get('category')
        tech_stack = request.form.get('tech_stack')
        description = request.form.get('description')
        url = request.form.get('url')
        image = request.files.get('image')
        project_id = request.form.get('project_id') # Will be present for edits

        if project_id: # Updating existing
            project = Project.query.get_or_404(project_id)
            project.title = title
            project.category = category
            project.tech_stack = tech_stack
            project.description = description
            project.project_url = url
            if image:
                project.image_file = save_picture(image)
            flash('Project updated successfully!', 'success')
        else: # Creating new
            if not title or not description or not image:
                flash('Required fields missing.', 'danger')
                return redirect(request.url)
            
            image_file = save_picture(image)
            project = Project(
                title=title, category=category, tech_stack=tech_stack,
                description=description, project_url=url, image_file=image_file
            )
            db.session.add(project)
            flash('Project deployed successfully!', 'success')

        db.session.commit()
        return redirect(url_for('upload_project'))

    # GET request: fetch all projects to display in the table
    projects = Project.query.order_by(Project.date_posted.desc()).all()
    unread_count = Contact.query.filter_by(status='New').count()
    return render_template('admin/upload_project.html', projects=projects, unread_count=unread_count)

    

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/project_images', picture_fn)
    
    # Save the file
    form_picture.save(picture_path)
    return picture_fn

@app.route('/clear-session')
def clear_session():
    session.clear()
    return "Session cleared! Now go to /admin/connect-gmail to pick the right account."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))






