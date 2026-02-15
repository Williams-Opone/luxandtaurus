from datetime import datetime
from project import db
from werkzeug.security import generate_password_hash, check_password_hash




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    service = db.Column(db.String(255), nullable=False) 


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, default="Admin") # <--- NEW
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 

    def set_password(self, password_text):
        """Call this when creating the admin to hash the password."""
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        """Call this during login to verify the password."""
        return check_password_hash(self.password, password_text)
    
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    service_type = db.Column(db.String(50), nullable=False) # e.g., "Web Dev", "Consulting"
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Internal Admin Fields
    status = db.Column(db.String(20), default='New') # New, Replied, Archived
    notes = db.Column(db.Text) # Your private notes about this lead

    def __repr__(self):
        return f"Contact('{self.name}', '{self.email}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # A short tagline like "FinTech Platform"
    category = db.Column(db.String(50), nullable=False) 
    # Store tech stack as a comma-separated string e.g., "Python, Flask, Stripe"
    tech_stack = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Store the filename of the image, not the image itself
    image_file = db.Column(db.String(100), nullable=False, default='default_project.jpg')
    project_url = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Project('{self.title}', '{self.category}')"
