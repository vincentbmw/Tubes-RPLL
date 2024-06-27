import pymongo
import os

def initialize(ATLAS_URI):
    """Menghubungkan ke MongoDB Atlas."""
    
    if not ATLAS_URI:
        raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")
    client = pymongo.MongoClient(ATLAS_URI)
    return client

def get_users_db():
    """Mendapatkan koneksi ke database untuk user."""
    ATLAS_URI =  os.getenv("ATLAS_URI")
    if not ATLAS_URI:
        raise Exception("'ATLAS_URI' is not set. Please set it in .env before continuing...")
    client = pymongo.MongoClient(ATLAS_URI)
    db = client['dogs']
    return db 