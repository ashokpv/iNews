from flask import Blueprint, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
from shared_func import common_functions

client = MongoClient("mongodb://localhost:27017/")
# database
db = client["iNews"]
# collection

news_routes = Blueprint('news_routes', __name__)


@news_routes.route("/fetch_headlines")
@jwt_required
def fetch_headerlines():
    news_headlines = db["news_headlines"].find({}, {'_id': False}).sort(
        'datetime',
        -1).limit(20)
    json_data, count = common_functions.collection_to_json(news_headlines)
    return jsonify(data=json_data, count=count), 200
