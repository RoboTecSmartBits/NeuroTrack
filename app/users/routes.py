from flask import Blueprint, request, jsonify
from ..models import User, db
from functools import wraps
import jwt
from flask import current_app, request, jsonify

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Authentication helper function
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorator

@users_bp.route('/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    return jsonify(current_user.to_dict()), 200

@users_bp.route('/profile', methods=['PUT'])
@token_required
def update_user(current_user):
    data = request.get_json()
    
    if 'nume' in data:
        current_user.nume = data['nume']
    
    if 'age' in data:
        current_user.age = data['age']
    
    if 'email' in data:
        emails = data['email'] if isinstance(data['email'], list) else [data['email']]
        current_user.set_emails(emails)
    
    if 'medicamente' in data:
        medicamente = data['medicamente'] if isinstance(data['medicamente'], list) else [data['medicamente']]
        current_user.set_medicamente(medicamente)
    
    if 'password' in data:
        current_user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': current_user.to_dict()
    }), 200
