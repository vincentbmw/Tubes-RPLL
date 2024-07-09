from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug.security import generate_password_hash
from controllers.database import get_users_db  

register_blueprint = Blueprint('register', __name__)

@register_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_users_db()
        users_collection = db['users'] 

        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            gender = request.form.get('gender')

            if not all([name, email, password, gender]): 
                return render_template('register.html', error='Missing required fields')

            existing_user = users_collection.find_one({'email': email})
            if existing_user:
                return render_template('register.html', error='Email already exists')

            hashed_password = generate_password_hash(password)

            if gender.lower() == 'male':
                profile_picture = "https://firebasestorage.googleapis.com/v0/b/gotravel-9fad0.appspot.com/o/profile_pictures%2Fmale.png?alt=media&token=ed087933-e6cb-4781-b952-67cdf37b8dad" 
            else:
                profile_picture = "https://firebasestorage.googleapis.com/v0/b/gotravel-9fad0.appspot.com/o/profile_pictures%2Ffemale.png?alt=media&token=4f6f872c-f971-42c8-b526-a39ac604ddb5" 

            new_user = {
                'name': name,
                'email': email,
                'password': hashed_password,
                'gender': gender,
                'chats': [],
                'profile_picture': profile_picture
            }
            users_collection.insert_one(new_user)

            return redirect(url_for('loginpage'))

        except Exception as e:
            return render_template('register.html', error=str(e))
    
    return render_template('register.html')
