import sys
import os

# 1. This tells Python to look for the 'project' folder correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Import your app and db from the project folder
from project import app, db

# 3. Guard the run command so Vercel doesn't crash
if __name__ == "__main__":
    app.run()