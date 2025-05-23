from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from ..models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not data or 'nume' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400

    # Normalize emails input
    emails = data['email'] if isinstance(data['email'], list) else [data['email']]

    # Check if any email is already taken
    for email in emails:
        existing_users = User.query.filter(User.emails.like(f'%{email}%')).all()
        for user in existing_users:
            if email in user.get_emails():
                return jsonify({'message': f'User with email {email} already exists'}), 400

    # Create new user
    new_user = User(
        nume=data['nume'],
        age=data.get('age')
    )
    
    new_user.set_password(data['password'])
    new_user.set_emails(emails)
    
    if 'medicamente' in data:
        medicamente = data['medicamente']
        medicamente_list = medicamente if isinstance(medicamente, list) else [medicamente]
        new_user.set_medicamente(medicamente_list)

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data['email']
    matching_users = User.query.filter(User.emails.like(f'%{email}%')).all()
    
    user = None
    for potential_user in matching_users:
        if email in potential_user.get_emails():
            user = potential_user
            break
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/init-db', methods=['GET'])
def init_db():
    db.create_all()
    return jsonify({'message': 'Database initialized successfully'}), 200
