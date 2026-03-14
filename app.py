from project import app,db

if __name__=='__main__':
    with app.app_context():
        db.create_all()  # This creates the tables if they don't exist
    
    