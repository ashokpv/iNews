from flask import Blueprint, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
from shared_func import common_functions
from flask import request
from bson import ObjectId
client = MongoClient("mongodb://localhost:27017/")
# database
db = client["iNews"]
# collection

news_routes = Blueprint('news_routes', __name__)


@news_routes.route("/fetch_headlines")
@jwt_required
def fetch_headerlines():
    news_headlines = db["news_headlines"].find({}).sort(
        'datetime',
        -1).limit(40)
    json_data, count = common_functions.collection_to_json(news_headlines)
    return jsonify(data=json_data, count=count), 200


@news_routes.route("/fetch_newsarticles", methods=['GET'])
@jwt_required
def fetch_newsarticles():
    category = request.args.get("category")
    news_articles = db["news_articles"].find({"category": category}
                                             ).sort(
        'datetime',
        -1).limit(40)
    json_data, count = common_functions.collection_to_json(news_articles)
    return jsonify(data=json_data, count=count), 200


