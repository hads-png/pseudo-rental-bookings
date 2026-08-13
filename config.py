import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secret-key-pseudo-booqable'
    
    db_url = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(basedir, 'pseudo_booqable.db')}"
    # SQLAlchemy 1.4+ compatibility for Postgres if URL uses postgres://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configurations
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
