import sys
import os

# Add the project root to the path, making 'src' a recognizable package.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == '__main__':
    main()
