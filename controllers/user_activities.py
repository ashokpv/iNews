from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from pymongo import MongoClient
from shared_func import common_functions
from flask import request
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
# database
db = client["iNews"]
# collection

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
