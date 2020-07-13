from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from pymongo import MongoClient
from shared_func import common_functions
from flask import request
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["iNews"]

user_activity = Blueprint('user_activity', __name__)


@user_activity.route("/user_like/<objectid:user_id>", methods=["POST"])
@jwt_required
def add_user_likes(user_id):
    if request.is_json:
        news_id = request.json["news_id"]
        category = request.json["category"]
    else:
        news_id = request.form["news_id"]
        category = request.form["category"]
    if not news_id:
        return jsonify(data={"message": "Invalid news id"}), 400
    news_id = ObjectId(news_id)
    likes_updated = db["user_activity"].update({"user_id": user_id},
                                               {"$addToSet": {
                                                   "news_ids." + category:
                                                       news_id
                                               }}, True)
    db["news_articles"].update({"_id": news_id}, {"$inc": {"Likes": 1}},
                               True)
    return jsonify(data={"message": "Updated user likes."}), 200


@user_activity.route("/user_interest/<objectid:user_id>", methods=["POST"])
@jwt_required
def add_user_interest(user_id):
    if request.is_json:
        sources = request.json["sources"]
        category = request.json["category"]
    else:
        sources = request.form["sources"]
        category = request.form["category"]
    if not sources:
        return jsonify(data={"message": "Invalid Sources"}), 400
    db["user_activity"].update({"user_id": user_id},
                               {"$addToSet": {
                                   "Category": {"$each": category},
                                   "Sources": {"$each": sources}
                               }}, True)
    return jsonify(data={"message": "Updated user Interests."}), 200


@user_activity.route("/user_analytics/<objectid:user_id>", methods=["GET"])
@jwt_required
def get_user_analytics(user_id):
    if not user_id:
        return jsonify(data={"message": "Invalid User"}), 400
    return_data = {}
    user_data = db["user_activity"].find_one({"user_id": user_id})
    for key, value in user_data["news_ids"].items():
        return_data[key] = len(value)
    return_data["user_liked_categories"] = user_data.get("Category", [])
    return_data["user_liked_sources"] = user_data.get("Sources", [])
    return jsonify(return_data), 200
