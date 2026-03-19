from flask import Blueprint, request, jsonify
from utils.database import Session
from models.users_model import User
from models.refresh_token_model import RefreshToken
from utils.extensions import limiter, bcrypt
from utils.jwt_authentication import generate_access_token, generate_refresh_token, get_refresh_token_expiry
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit('5 per minute')
def register():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided.'}), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Missing required fields.'}), 400
    
    session = Session()

    try:
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Email already exists.'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(name=name, email=email, password=hashed_password)

        session.add(new_user)
        session.commit()

        access_token = generate_access_token(new_user.id)
        refresh_token = generate_refresh_token()

        new_refresh_token = RefreshToken(
            user_id = new_user.id,
            token = refresh_token,
            expires_at = get_refresh_token_expiry()
        )

        session.add(new_refresh_token)
        session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': new_refresh_token
        }), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occured', 'error': str(e)}), 500
    finally:
        session.close()
        
@auth_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided.'}), 400
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    session = Session()

    try:
        user = session.query(User).filter_by(email=email).first()

        if not user:
            return jsonify({'massge': "Invalid email or password"}), 401
        
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        access_token = generate_access_token(user.id)
        refresh_token = generate_refresh_token()

        new_refresh_token = RefreshToken(
            user_id = user.id,
            token = refresh_token,
            expires_at = get_refresh_token_expiry()
        )

        session.add(new_refresh_token)
        session.commit()

        return jsonify({
            'message': "Login successful.",
            'access_token': access_token,
            'refresh_token': new_refresh_token
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occured', 'error': str(e)}), 500
    finally:
        session.close()
    
@auth_bp.route('/refresh', methods=['POST'])
@limiter.limit('10 per minute')
def refresh():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided.'}), 400
    
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'message': 'Invalid refresh token'}), 400
    
    session = Session()

    try:
        token_record = session.query(RefreshToken).filter_by(token=refresh_token).first()

        if not token_record:
            return jsonify({'message': 'Invalid refresh token'}), 400
        
        if token_record.expires_at < datetime.utcnow():
            session.delete(token_record)
            session.commit()
            return jsonify({'message': 'Refresh token expired, please login again.'}), 400
        
        new_access_token = generate_access_token(token_record.user_id)

        return jsonify({'access_token': new_access_token}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occured', 'error': str(e)}), 500
    finally:
        session.close()

@auth_bp.route('/logout', methods=['POST'])
@limiter.limit('10 per minute')
def logout():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided.'}), 400 
    
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'message': 'Invalid refresh token'}), 400
    
    session = Session()

    try:
        token_record = session.query(RefreshToken).filter_by(token=refresh_token).first()

        if not token_record:
            return jsonify({'message': 'Invalid refresh token'}), 401
        
        session.delete(token_record)
        session.commit()

        return jsonify({'message': 'Logout successful.'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occured', 'error': str(e)}), 500
    finally:
        session.close()





