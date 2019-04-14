from pymongo import MongoClient

client = MongoClient('mongodb://{}:27017'.format("localhost"))
db = client.Resetera

def get_collection(collection):
    return db[collection]