import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # ДОЛЖНО БЫТЬ SQLite для простоты
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'sto_plus.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Остальные настройки...