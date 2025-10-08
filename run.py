"""
Production entry point for Concierge Bank API
Runs with Granian ASGI server for high performance

Usage:
  Development: python app.py
  Production:  granian --interface asgi app:app --host 0.0.0.0 --port 5000 --workers 2
"""
from app import app

__all__ = ['app']
