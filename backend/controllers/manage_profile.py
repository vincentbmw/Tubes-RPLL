from flask import Blueprint, request, jsonify, session
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from controllers.database import get_users_db

manage_profile_blueprint = Blueprint('manage_profile', __name__)
USERS_COLLECTION_NAME = 'users'

@manage_profile_blueprint.route('/api/manage_profile', methods=['PUT'])
def update_user():
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        update_data = {}

        if 'name' in data:
            update_data['name'] = data['name']
        if 'email' in data:
            update_data['email'] = data['email']
        if 'password' in data:
            update_data['password'] = generate_password_hash(data['password']) 
        if 'gender' in data:
            update_data['gender'] = data['gender']
            if data['gender'].lower() == 'male':
                update_data['profile_picture'] = "https://firebasestorage.googleapis.com/v0/b/gotravel-9fad0.appspot.com/o/profile_pictures%2Fmale.png?alt=media&token=ed087933-e6cb-4781-b952-67cdf37b8dad"
            else: 
                update_data['profile_picture'] = "https://firebasestorage.googleapis.com/v0/b/gotravel-9fad0.appspot.com/o/profile_pictures%2Ffemale.png?alt=media&token=4f6f872c-f971-42c8-b526-a39ac604ddb5" 

        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

        if result.modified_count == 1:
            return jsonify({'message': 'User profile updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500