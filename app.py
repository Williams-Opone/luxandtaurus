import sys
import os

# DEBUG - remove after fixing
print("=== VERCEL DEBUG ===")
print("Current working directory:", os.getcwd())
print("__file__ location:", os.path.abspath(__file__))
print("sys.path:", sys.path)
print("Files in /var/task:", os.listdir('/var/task'))
print("=== END DEBUG ===")

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from project import app