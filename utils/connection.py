from pymongo import MongoClient
DB = None

def setup_connection(mongo_uri):
    global DB
    client = MongoClient(mongo_uri)
    DB = client.Resetera

def get_collection(collection):
    return DB[collection]