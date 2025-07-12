#!/usr/bin/env python3
"""
Super minimal test - step by step
"""
print("Test 1: Basic imports")
import sys
import os

print("Test 2: Flask import")
from flask import Flask

print("Test 3: SQLAlchemy import")  
from flask_sqlalchemy import SQLAlchemy

print("Test 4: Direct extension creation")
db = SQLAlchemy()

print("Test 5: Minimal app creation")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minimal.db'
app.config['SECRET_KEY'] = 'test'

print("Test 6: DB initialization")
db.init_app(app)

print("✅ Minimal app works!")
