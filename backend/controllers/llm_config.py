import os
from llama_index.embeddings.google import GooglePaLMEmbedding
from llama_index.core import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from controllers.database import get_users_db
from controllers.chats import save_chat, save_to_previous_chat

# LLM Configuration
service_context = None
vector_store = None
storage_context = None
index = None
DB_NAME = 'dogs'
COLLECTION_NAME = 'type'
USERS_COLLECTION_NAME = "users"

def setup_llm(api_key):
    global service_context 

    model_name = "models/embedding-gecko-001"
    os.environ["GOOGLE_API_KEY"] = api_key
    
    Settings.embed_model = GooglePaLMEmbedding(model_name=model_name, api_key=api_key)
    Settings.llm = Gemini(model="models/gemini-1.5-pro", temperature=0.7, system_prompt="""
    Anda adalah asisten chatbot yang membantu pengguna dalam mencari informasi tentang anjing.
    Selalu jawab pertanyaan pengguna dalam Bahasa Indonesia yang baik dan benar.                      
    """)
    service_context = ServiceContext.from_defaults(embed_model=Settings.embed_model, llm=Settings.llm)


def connect_llm(client):
    global index
    vector_store = MongoDBAtlasVectorSearch(
        mongodb_client=client,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        index_name='idx_embedding'
    )
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

def run_query(text, user_id, chat_id=None):
    global index

    response = index.as_query_engine().query(text)

    if chat_id:
        save_to_previous_chat(user_id, text, str(response), chat_id)
    else:
        save_chat(user_id, text, str(response))

    return response