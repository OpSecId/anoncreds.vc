import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    
    DOMAIN = os.getenv('DOMAIN', 'localhost')
    ENDPOINT = f"https://{DOMAIN}"
    
    
    ASKAR_DB = os.getenv('ASKAR_DB', 'sqlite://app.db')
    SESSION_COOKIE_NAME  = 'PyDentity'
    
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_HTTPONLY = 'True'
    
    # AGENT_ADMIN_API_KEY = os.getenv('AGENT_ADMIN_API_KEY')
    AGENT_ADMIN_ENDPOINT = os.getenv('AGENT_ADMIN_ENDPOINT')
    
    DIDWEBVH_SERVER = os.getenv('DIDWEBVH_SERVER', None)
    DIDWEBVH_WITNESS_KEY = os.getenv('DIDWEBVH_WITNESS_KEY', None)
    
    SECRET_KEY = os.getenv('SECRET_KEY')
    