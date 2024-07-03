import os
from llama_index.embeddings.google import GooglePaLMEmbedding
from llama_index.core import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from controllers.chats import PreviousChatSaver, NewChatSaver

# LLM Configuration
service_context = None
vector_store = None
storage_context = None
index = None
DB_NAME = 'dogs'
COLLECTION_NAME = 'type'

def setup_llm(api_key):
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
        saver = PreviousChatSaver()
    else:
        saver = NewChatSaver()

    saver.save(user_id, text, str(response), chat_id)
    print("Pesan berhasil disimpan ke database")

    return response