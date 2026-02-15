
from datetime import datetime

# Flask & Extensions
from flask import render_template, request, flash, session, redirect, url_for, jsonify
from flask_mail import Message


# IMPORTANT: Import 'csrf' here so we can disable it for the reply button
from project import app, mail, csrf,db
from .model import User,Project,Contact


# --- ROUTES ---

@app.route('/')
def home():
    return render_template('user/home.html')

@app.route('/agency/')
def agency():
    year = 2023
    month = 5
    day = 15
    current_date = datetime.now()
    provided_date = datetime(year, month, day)
    
    years = current_date.year - provided_date.year
    months = current_date.month - provided_date.month
    days = current_date.day - provided_date.day

    if days < 0:
        months -= 1
        days += 30 
    if months < 0:
        years -= 1
        months += 12
    
    return render_template('user/agency.html' , years = years)

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        service = request.form.get('service')
        # Since your Contact model requires a 'message', we'll provide a default
        message_body = f"Interested in {service}"

        try:
            # 1. Save to the CONTACT table (This fixes your Admin Panel issue)
            new_contact = Contact(
                name=name, 
                email=email, 
                service_type=service, 
                message=message_body
            )
            db.session.add(new_contact)
            
            # Optional: Also update the User table if you want to keep a directory
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                existing_user.name = name
                existing_user.service = service
            else:
                new_user = User(name=name, email=email, service=service)
                db.session.add(new_user)

            db.session.commit()

            # 2. Notifications
            admin_msg = Message(
                subject=f"New Project Request: {service}",
                recipients=['williamsopone3@gmail.com'],
                body=f"Protocol Initiated:\nName: {name}\nEmail: {email}\nService: {service}"
            )
            mail.send(admin_msg)

            flash("Protocol initiated successfully!", "success")
            return redirect(url_for('home', _anchor='contact'))

        except Exception as e:
            db.session.rollback()
            print(f"CRITICAL ERROR: {e}") 
            flash("System error. Please try again.", "danger")
            return redirect(url_for('home', _anchor='contact'))

    return render_template('user/home.html')

@app.route('/project')
def project():
    # Fetch all projects, ordered by date (newest first)
    projects = Project.query.order_by(Project.date_posted.desc()).all()
    return render_template('user/project.html', projects=projects)

@app.route('/policy/')
def policy():
    return render_template('user/policy.html')

@app.route('/terms/')
def terms():
    return render_template('user/terms.html') 

