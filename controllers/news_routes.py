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
        -1).limit(100)
    json_data, count = common_functions.collection_to_json(news_headlines)
    return jsonify(data=json_data, count=count), 200


@news_routes.route("/fetch_newsarticles/<objectid:user_id>", methods=['GET'])
@jwt_required
def fetch_newsarticles(user_id):
    category = request.args.get("category")
    news_articles = db["news_articles"].find({"category": category,
                                              "images": {"$ne": None}}
                                             ).sort(
        'datetime',
        -1).limit(100)
    user_likes = db["user_activity"].aggregate([
        {"$match": {"user_id": user_id}},
        {"$addFields": {
            "news_ids": {
                "$map": {
                    "input": {"$objectToArray": "$news_ids"},
                    "as": "el",
                    "in": "$$el.v"
                }
            }}
        },
        {"$project": {
            "user_id": 1,
            "news_ids": {"$reduce": {
                "input": '$news_ids',
                "initialValue": [],
                "in": {"$concatArrays": ['$$value', '$$this']}
            }}
        }}
    ])
    user_like_data = common_functions.aggregate_to_json(user_likes,
                                                        attribute="news_ids")
    json_data, count = common_functions.collection_to_json(news_articles)
    return jsonify(data=json_data, count=count, user_likes=user_like_data), 200


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
        if user_categories.get("Category", ""):
            news_articles = db["news_articles"].find(
                {"category": {"$in": user_categories["Category"]}}
            ).sort(
                'datetime',
                -1).limit(100)
        else:
            news_articles = db["news_articles"].find(
                {"images": {"$ne": None}}
            ).sort(
                'datetime',
                -1).limit(100)
    json_data, count = common_functions.collection_to_json(news_articles)
    return jsonify(data=json_data, count=count), 200
