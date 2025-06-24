# api/conftest.py
import sys
import os

# this file lives at .../Big_Data_Project/api/conftest.py
HERE = os.path.dirname(__file__)
SRC  = os.path.join(HERE, "src")

# Prepend src/ so that 'import stream_api' works
if SRC not in sys.path:
    sys.path.insert(0, SRC)