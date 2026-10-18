#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    print("Creating missing tables...")
    db.create_all()
    print("Tables created!")
    print("\nDone!")