import jwt
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify 
from flask_limiter.util import get_remote_address

SECRET_KEY = os.getenv('SECRET_KEY')

# ACCESS TOKEN
# -------------------------------------------------------------------------

def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': datetime.now() + timedelta(days=1)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# REFRESH TOKEN
# -------------------------------------------------------------------------

def generate_refresh_token():
    return secrets.token_hex(64)

def get_refresh_token_expiry():
    return datetime.utcnow() + timedelta(days=7)
    

# LIMITER HELPER
# -------------------------------------------------------------------------

def get_current_user_id():
    try:
        auth_header = request.headers['Authentication']
        
        if not auth_header:
            return get_remote_address()
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return get_remote_address()
        
        return payload['user_id']
    
    except:
        return get_remote_address()


# DECORATOR
# -------------------------------------------------------------------------    

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1] if " " in auth_header else None

        if not token:
            return jsonify({'message': 'Unauthorized'}), 401
        
        payload = verify_token(token)

        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        return f(payload['user_id'], *args, **kwargs)
    
    return decorated