from pymongo import MongoClient
import os

URL = 'mongodb://localhost:27017/'
# URL = os.environ.get('MONGO_URL')

def connection_client():
    client = MongoClient(URL)
    db = client['coronavirus']
    return db

