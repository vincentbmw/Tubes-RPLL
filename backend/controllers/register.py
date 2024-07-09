<<<<<<< HEAD
<<<<<<< Updated upstream
from flask import Blueprint, request, jsonify
=======
from flask import Blueprint, request, render_template, redirect, url_for, flash
>>>>>>> Stashed changes
=======
from flask import Blueprint, request, render_template, redirect, url_for
>>>>>>> e83a98d14695282989988df74464a651f63f0b8d
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

<<<<<<< HEAD
<<<<<<< Updated upstream
        if not all([name, email, password, gender]): 
            return jsonify({'error': 'Missing required fields'}), 400

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
=======
            if not all([name, email, password, gender]): 
                flash('Missing required fields', 'error') # flash message
                return redirect(url_for('registerpage'))

            existing_user = users_collection.find_one({'email': email})
            if existing_user:
                flash('Email already exists', 'error')
                return redirect(url_for('registerpage'))
>>>>>>> Stashed changes
=======
            if not all([name, email, password, gender]): 
                return render_template('register.html', error='Missing required fields')

            existing_user = users_collection.find_one({'email': email})
            if existing_user:
                return render_template('register.html', error='Email already exists')
>>>>>>> e83a98d14695282989988df74464a651f63f0b8d

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

<<<<<<< HEAD
<<<<<<< Updated upstream
    except Exception as e:
        return jsonify({'error': str(e)}), 500
=======
        except Exception as e:
            flash(str(e), 'error') # flash message
            return redirect(url_for('registerpage'))
    
    return render_template('register.html')
>>>>>>> Stashed changes
=======
        except Exception as e:
            return render_template('register.html', error=str(e))
    
    return render_template('register.html')
>>>>>>> e83a98d14695282989988df74464a651f63f0b8d
