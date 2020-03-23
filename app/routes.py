from app import app
from pymongo import MongoClient
from flask import jsonify


URL = 'mongodb://localhost:27017/'
client = MongoClient(URL)
db = client['coronavirus']


@app.route('/')
def index():
    return "Please visit /api/all"

@app.route('/api/all')
def api_all():
    data = db.datos.find()
    new_data = []
    for dt in data:
        dt['_id'] = str(dt['_id'])
        new_data.append(dt)

    return jsonify({"result": new_data})