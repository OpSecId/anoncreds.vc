import os
import time
from pathlib import Path
from dotenv import load_dotenv
from cachelib.file import FileSystemCache

load_dotenv()
Path("session").mkdir(parents=True, exist_ok=True)

class Config(object):
    
    APP_TITLE = 'AnonCreds + WebVH'
    
    DOMAIN = os.getenv('DOMAIN', 'localhost:5000')
    ENDPOINT = f"http://{DOMAIN}" if DOMAIN == 'localhost:5000' else f"https://{DOMAIN}"
    
    
    ASKAR_DB = os.getenv('ASKAR_DB', 'sqlite://session/app.db')
    
    
    SESSION_TYPE = 'cachelib'
    SESSION_SERIALIZATION_FORMAT = 'json'
    SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="session")
    SESSION_COOKIE_NAME  = 'AnonCreds'
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_HTTPONLY = 'True'
    
    # AGENT_ADMIN_API_KEY = os.getenv('AGENT_ADMIN_API_KEY')
    AGENT_ADMIN_ENDPOINT = os.getenv('AGENT_ADMIN_ENDPOINT')
    
    DIDWEBVH_SERVER = os.getenv('DIDWEBVH_SERVER', None)
    DIDWEBVH_WITNESS_KEY = os.getenv('DIDWEBVH_WITNESS_KEY', None)
    
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    DEMO = {
        'name': 'Meeting Invitation',
        'version': '1.1',
        'issuer': 'WebVH AnonCreds Demo',
        'size': 100,
        'preview': {
            'group': 'OWL',
            'email': 'jane.doe@example.com',
            'date': '20250213'
        },
        'request': {
            'attributes': ['group', 'email'],
            'predicate': ['date', '>=', 20250101],
        }
    }
    