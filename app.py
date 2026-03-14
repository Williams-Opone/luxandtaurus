import sys
import os

# This forces Vercel to see the 'project' folder sitting right next to app.py
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from project import app, db
except ImportError:
    # This is a backup in case Vercel's working directory is different
    sys.path.append(os.getcwd())
    from project import app, db

if __name__ == "__main__":
    app.run()