from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from database import get_users_db  

register_blueprint = Blueprint('register', __name__)

@register_blueprint.route('/api/register', methods=['POST'])
def register():
    db = get_users_db()
    users_collection = db['credentials'] 

    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        gender = data.get('gender')

        if not all([name, email, password, gender]): 
            return jsonify({'error': 'Missing required fields'}), 400

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        hashed_password = generate_password_hash(password)

        # Tentukan URL gambar profil berdasarkan gender
        if gender.lower() == 'male':
            profile_picture = "https://firebasestorage.googleapis.com/v0/b/gotravel-9fad0.appspot.com/o/profile_pictures%2Fmale.png?alt=media&token=ed087933-e6cb-4781-b952-67cdf37b8dad" 
        elif gender.lower() == 'female':
            profile_picture = "https://firebasestorage.googleapis.com/v0/b/<your-firebase-project-id>.appspot.com/o/profile_pictures%2Ffemale.png?alt=media&token=<your-token>" 
        else:
            profile_picture = "https://example.com/default_profile.png" # Ganti dengan URL default

        new_user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'gender': gender,
            'chats': [],
            'profile_picture': profile_picture
        }
        users_collection.insert_one(new_user)

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500