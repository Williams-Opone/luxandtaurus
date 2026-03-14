import sys
import os

# Force-add the directory containing app.py to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from project import app

if __name__ == "__main__":
    app.run()