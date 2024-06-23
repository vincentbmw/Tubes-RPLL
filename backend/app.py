# Import libraries
import os
import sys
import pymongo
from urllib.request import urlopen
sys.path.insert(0, '../')
from dotenv import find_dotenv, dotenv_values
from llama_index.embeddings.google import GooglePaLMEmbedding
from llama_index.core import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from pyngrok import ngrok

app = Flask(__name__)

# Define variables
DB_NAME = 'dogs'
COLLECTION_NAME = 'type'
USERS_COLLECTION_NAME = 'credentials'
config = dotenv_values(find_dotenv())
service_context = None
vector_store = None
storage_context = None
index = None

# Initialization function
def initialize():
    ATLAS_URI = config.get('ATLAS_URI')
    print(f"ATLAS_URI detected is: {ATLAS_URI}")

    if not ATLAS_URI:
        raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")

    os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

    mongodb_client = pymongo.MongoClient(ATLAS_URI)
    print('Atlas client successfully initialized!')
    return mongodb_client

# Fungsi untuk mendapatkan koneksi MongoDB untuk user
def get_users_db():
    ATLAS_URI = config.get('ATLAS_URI')
    if not ATLAS_URI:
        raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")
    client = pymongo.MongoClient(ATLAS_URI)
    db = client[DB_NAME]
    return db

# LLM Function
def setup_llm():
    model_name = "models/embedding-gecko-001"
    api_key = config.get('GOOGLE_API_KEY')
    os.environ["GOOGLE_API_KEY"] = api_key
    
    Settings.embed_model = GooglePaLMEmbedding(model_name=model_name, api_key=api_key)
    Settings.llm = Gemini(model="models/gemini-1.5-pro", temperature=0.7, system_prompt="""
    You are an efficient language model designed to respond promptly to user inquiries.
    Responses should be concise and to the point, avoiding unnecessary elaboration unless requested by the user.
    Remember to give another dog breeds if users didn't like it                      
    """)
    resp = Settings.llm.complete("Paul Graham is ")
    print(resp)
    global service_context
    service_context = ServiceContext.from_defaults(embed_model=Settings.embed_model, llm=Settings.llm)

# Connect LLM to MongoDB
def connect_llm(client):
    global index
    vector_store = MongoDBAtlasVectorSearch(mongodb_client=client,
                                            db_name=DB_NAME, collection_name=COLLECTION_NAME,
                                            index_name='idx_embedding')
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

# Query function
def run_query(text):
    response = index.as_query_engine().query(text)
    return response

@app.route('/api/register', methods=['POST'])
def register():
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

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
        else:
            profile_picture = "https://firebasestorage.googleapis.com/v0/b/<your-firebase-project-id>.appspot.com/o/profile_pictures%2Ffemale.png?alt=media&token=<your-token>" 

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

@app.route('/api/login', methods=['POST'])
def login():
    db = get_users_db()
    users_collection = db[USERS_COLLECTION_NAME]

    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        session['user_id'] = str(user['_id'])
        
        return jsonify({'message': 'Login successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/query', methods=['POST'])
def api_query():
    try:
        data = request.get_json()
        query_text = data.get('query')
        if not query_text:
            return jsonify({'error': 'Missing "query" parameter'}), 400

        response = run_query(query_text)
        return jsonify({'response': str(response)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    ip = urlopen('https://api.ipify.org').read().decode('utf-8')
    print(f"My public IP is '{ip}'. Make sure this IP is allowed to connect to cloud Atlas")
    mongodb_client = initialize()
    setup_llm()
    connect_llm(mongodb_client)
    public_url = ngrok.connect(5000).public_url
    print(f"ngrok tunnel opened at {public_url}")
    app.run()