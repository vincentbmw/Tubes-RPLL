import pymongo
import os
from flask import jsonify, session
from bson.objectid import ObjectId
from dotenv import find_dotenv, dotenv_values

config = dotenv_values(find_dotenv())

# --- Simple Factory Pattern ---

class Database:
    def __init__(self, uri):
        self.client = pymongo.MongoClient(uri)

    def get_db(self, db_name):
        return self.client[db_name]

class DatabaseFactory:
    @staticmethod
    def create():
        atlas_uri = config.get('ATLAS_URI')
        if not atlas_uri:
            raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")
        return Database(atlas_uri)

def initialize():
    ATLAS_URI = config.get('ATLAS_URI')
    print(f"ATLAS_URI detected is: {ATLAS_URI}")

    if not ATLAS_URI:
        raise Exception ("'ATLAS_URI' is not set. Please set it in .env before continuing...")

    os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

    mongodb_client = pymongo.MongoClient(ATLAS_URI)
    print ('Atlas client succesfully initialized!')
    return mongodb_client

def get_users_db():
    """Mendapatkan database 'users'."""
    db_factory = DatabaseFactory.create()
    return db_factory.get_db('dogs') 

def get_user_profile_data():
    db = get_users_db()
    users_collection = db['users']

    try:
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401 

        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return {'error': 'User not found'}, 404

        profile_data = {
            'profile_picture': user.get('profile_picture'),
            'username': user.get('name'),
            'gender': user.get('gender')
        }

        return profile_data, 200

    except Exception as e:
        return {'error': str(e)}, 500