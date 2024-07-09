from flask import Blueprint, request, session, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from controllers.database import get_users_db  

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_users_db()
        users_collection = db['users']  

        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if not all([email, password]):
                return render_template('login.html', error='Missing email or password')

            user = users_collection.find_one({'email': email})
            if not user:
                return render_template('login.html', error='Please check your password and email!')

            if not check_password_hash(user['password'], password):
                return render_template('login.html', error='Please check your password and email!')

            session['user_id'] = str(user['_id'])
            
            return redirect(url_for('chatpage'))

        except Exception as e:
            return render_template('login-page.html', error=str(e))
    
    return render_template('login-page.html')
