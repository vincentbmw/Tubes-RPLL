import datetime
import uuid
from flask import Blueprint, jsonify, session
from bson.objectid import ObjectId
from controllers.database import get_users_db

chats_blueprint = Blueprint('get_chats', __name__)
USERS_COLLECTION_NAME = "users"

@chats_blueprint.route('/api/chats', methods=['GET'])
def get_chats():
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        chat_list = []
        for chat in user.get('chats', []):
            first_prompt = chat.get('prompts', [{}])[0].get('user', '') 
            chat_list.append({
                'chatId': chat.get('chatId'),
                'firstPrompt': first_prompt,
            })

        return jsonify({'chats': chat_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_to_previous_chat(user_id, user_message, bot_response, chat_id=None):
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        if chat_id: 
            result = users_collection.update_one(
                {
                    '_id': ObjectId(user_id), 
                    'chats.chatId': chat_id 
                },
                {
                    '$push': {
                        'chats.$.prompts': {
                            "user": user_message,
                            "bot": bot_response
                        }
                    }
                }
            )

            if result.modified_count == 0:
                print(f"Error: Chat with ID {chat_id} not found for user {user_id}")  
                return
        else:
            print(f"Error: Need Chat ID before saving")  
            return

        if result.modified_count == 0:
            print(f"Error: User with ID {user_id} not found!")  
    except Exception as e:
        print(f"Error saving chat: {str(e)}")

def save_chat(user_id, user_message, bot_response):
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$push': {
                    'chats': {
                        "chatId": str(uuid.uuid4()), 
                        "createdAt": datetime.datetime.utcnow(),
                        "prompts": [
                            {"user": user_message, "bot": bot_response}
                        ]
                    }
                }
            }
        )

        if result.modified_count == 0:
            print(f"Error: User with ID {user_id} not found!")  
    except Exception as e:
        print(f"Error saving chat: {str(e)}")

def get_chat_prompts(chat_id):
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        user = users_collection.find_one(
            {'_id': ObjectId(user_id), 'chats.chatId': chat_id},
            {'chats.$': 1}
        )

        if not user:
            return jsonify({'error': 'Chat not found'}), 404

        chat = user.get('chats', [{}])[0]
        prompts = chat.get('prompts', []) 

        return {'prompts': prompts}, 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500