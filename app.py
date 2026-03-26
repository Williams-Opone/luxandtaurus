import os
import sys

# 1. FIX THE PATH IMMEDIATELY (Must be before 'from project import...')
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 2. NOW IMPORT YOUR APP AND DB
try:
    from project import app, db
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    raise

# Vercel needs 'app' to be available at the module level
# We use this for the server to find the Flask instance
handler = app 

if __name__ == '__main__':
    with app.app_context():
        # This creates tables in your database
        db.create_all()
        print("Database tables synchronized!")
    app.run(debug=True)