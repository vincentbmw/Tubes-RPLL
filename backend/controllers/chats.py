import datetime
import uuid
from flask import Blueprint, jsonify, session
from bson.objectid import ObjectId
from controllers.database import get_users_db
from abc import ABC, abstractmethod

chats_blueprint = Blueprint('get_chats', __name__)
USERS_COLLECTION_NAME = "users"

# --- Repository Pattern ---

class ChatRepository:
    def __init__(self, db):
        self.collection = db[USERS_COLLECTION_NAME]

    def get_chats_by_user_id(self, user_id):
        user = self.collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return None
        return user.get('chats', [])
    
    def update_previous_chat(self, user_id, chat_id, user_message, bot_response):
        """Menambahkan prompt baru ke chat yang sudah ada."""
        result = self.collection.update_one(
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
        return result.modified_count > 0
    
    def save_chat(self, user_id, chat_data):
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'chats': chat_data}}
        )
        return result.modified_count > 0

# --- Strategy Pattern ---

class ChatSaver(ABC):
    @abstractmethod
    def save(self, user_id, user_message, bot_response, chat_id=None):
        pass

class PreviousChatSaver(ChatSaver):
    def save(self, user_id, user_message, bot_response, chat_id):
        print(f"PreviousChatSaver - user_id: {user_id}, chat_id: {chat_id}") 
        db = get_users_db()
        repository = ChatRepository(db)

        success = repository.update_previous_chat(user_id, chat_id, user_message, bot_response)

        if not success:
            print(f"Error: Chat with ID {chat_id} not found for user {user_id}")

class NewChatSaver(ChatSaver):
    def save(self, user_id, user_message, bot_response, chat_id=None):
        db = get_users_db()
        repository = ChatRepository(db)
        new_chat = {
            "chatId": str(uuid.uuid4()),
            "createdAt": datetime.datetime.utcnow(),
            "prompts": [
                {"user": user_message, "bot": bot_response}
            ]
        }
        return repository.save_chat(user_id, new_chat)

# --- Route Handlers ---

@chats_blueprint.route('/api/chats', methods=['GET'])
def get_chats():
    db = get_users_db()
    repository = ChatRepository(db)  

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        chats = repository.get_chats_by_user_id(user_id)
        if chats is None:
            return jsonify({'error': 'User not found'}), 404

        chat_list = []
        for chat in chats:
            first_prompt = chat.get('prompts', [{}])[0].get('user', '')
            chat_list.append({
                'chatId': chat.get('chatId'),
                'firstPrompt': first_prompt,
            })

        return jsonify({'chats': chat_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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