from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash
from controllers.database import get_users_db  

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['POST'])
def login():
    db = get_users_db()
    users_collection = db['users']  

    try:
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([email, password]):
            return jsonify('login-page.html', error='Missing email or password'), 400

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify('login-page.html', error= 'Invalid credentials'), 401

        if not check_password_hash(user['password'], password):
            return jsonify('login-page.html', error= 'Invalid credentials'), 401

        session['user_id'] = str(user['_id'])
        
        return redirect(url_for('chatpage'))

    except Exception as e:
        return jsonify('login-page.html', error= str(e)), 500