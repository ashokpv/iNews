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
        -1).limit(60)
    json_data, count = common_functions.collection_to_json(news_articles)
    return jsonify(data=json_data, count=count), 200


@news_routes.route("/fetch_newsrecommendation/<objectid:user_id>", methods=[
    'GET'])
@jwt_required
def fetch_newsrecommendation(user_id):
    news_id = db["user_recommendation"].find_one({"user_id": user_id})
    if news_id:
        ids = list()
        for key, value in news_id["recommendation"].items():
            ids = ids + value
        news_articles = db["news_articles"].find({"_id": {"$in": ids}}
                                                 ).sort('datetime',
                                                        -1).limit(60)
    else:
        user_categories = db["user_activity"].find_one({"user_id": user_id})

        news_articles = db["news_articles"].find(
            {"category": {"$in": user_categories["Category"]}}
            ).sort(
            'datetime',
            -1).limit(60)
    json_data, count = common_functions.collection_to_json(news_articles)
    return jsonify(data=json_data, count=count), 200
