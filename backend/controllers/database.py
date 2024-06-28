import pymongo
import os
from flask import jsonify, session
from bson.objectid import ObjectId

def initialize(ATLAS_URI):
    if not ATLAS_URI:
        raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")
    client = pymongo.MongoClient(ATLAS_URI)
    return client

def get_users_db():
    ATLAS_URI =  os.getenv("ATLAS_URI")
    if not ATLAS_URI:
        raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")
    client = pymongo.MongoClient(ATLAS_URI)
    db = client['dogs']
    return db

def get_user_profile_data():
    db = get_users_db()
    users_collection = db['users']

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404 

        profile_data = {
            'profile_picture': user.get('profile_picture'),
            'username': user.get('name')
        }

        return profile_data, 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500