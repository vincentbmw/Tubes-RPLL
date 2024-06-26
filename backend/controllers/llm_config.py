import os
from llama_index.embeddings.google import GooglePaLMEmbedding
from llama_index.core import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
import pymongo
import datetime
import uuid

# LLM Configuration
service_context = None
vector_store = None
storage_context = None
index = None
DB_NAME = 'dogs'
COLLECTION_NAME = 'type'
USERS_COLLECTION_NAME = "users"

def setup_llm(api_key):
    """Menyiapkan Google Gemini LLM dan embedding."""
    global service_context 

    model_name = "models/embedding-gecko-001"
    os.environ["GOOGLE_API_KEY"] = api_key
    
    Settings.embed_model = GooglePaLMEmbedding(model_name=model_name, api_key=api_key)
    Settings.llm = Gemini(model="models/gemini-1.5-pro", temperature=0.7, system_prompt="""
    You are an efficient language model designed to respond promptly to user inquiries.
    Responses should be concise and to the point, avoiding unnecessary elaboration unless requested by the user.
    Remember to give another dog breeds if users didn't like it                      
    """)
    service_context = ServiceContext.from_defaults(embed_model=Settings.embed_model, llm=Settings.llm)


def connect_llm(client):
    """Menghubungkan LLM ke MongoDB Vector Store."""
    global index
    vector_store = MongoDBAtlasVectorSearch(
        mongodb_client=client,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        index_name='idx_embedding'
    )
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

def run_query(text, user_id): 
    """Menjalankan query pada LLM dan menyimpan chat."""
    global index

    response = index.as_query_engine().query(text)

    save_chat(user_id, text, str(response)) 

    return response

def get_users_db():
    """Mendapatkan koneksi ke database user."""
    client = pymongo.MongoClient(ATLAS_URI)
    db = client[DB_NAME]
    return db

def save_chat(user_id, user_message, bot_response):
    """Menyimpan chat ke database user."""
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            print(f"Error: User with ID {user_id} not found!")  
            return

        new_chat = {
            "chatId": str(uuid.uuid4()), 
            "createdAt": datetime.datetime.utcnow(),
            "prompts": [
                {"user": user_message, "bot": bot_response}
            ]
        }

        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'chats': new_chat}}
        )

    except Exception as e:
        print(f"Error saving chat: {str(e)}") 