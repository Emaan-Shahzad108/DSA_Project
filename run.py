import os
import sys

# Add project root to Python's module search path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.main_window import main

if __name__ == "__main__":
    main()