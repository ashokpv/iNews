from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
import bcrypt
from datetime import datetime
from controllers import news_routes

# Making a Connection with MongoClient
client = MongoClient("mongodb://localhost:27017/")
# database
db = client["iNews"]
# collection
user = db["User"]
app = Flask(__name__)
jwt = JWTManager(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = "JWTSECRETCHECK"


@app.route("/dashboard")
@jwt_required
def dasboard():
    return jsonify(message="Welcome! to the Data Science Learner")


@app.route("/register", methods=["POST"])
def register():
    if request.is_json:
        email = request.json["email"]
    else:
        email = request.form["email"]
    test = user.find_one({"email": email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        if request.is_json:
            first_name = request.json["first_name"]
            last_name = request.json["last_name"]
            password = request.json["password"]
        else:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            password = request.form["password"]
        hashpass = bcrypt.hashpw(password.encode('utf-8'),
                                 bcrypt.gensalt())

        print(hashpass)
        user_info = dict(first_name=first_name, last_name=last_name,
                         email=email, password=hashpass,
                         createtedAt=datetime.now())
        user.insert_one(user_info)
        return jsonify(message="User added sucessfully."), 201


@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = user.find_one(
        {"email": email})
    if bcrypt.hashpw(password.encode('utf-8'),
                     test['password']) == test['password'] and test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login Succeeded!",
                       username=test["first_name"],
                       access_token=access_token), 201
    else:
        return jsonify(message="Invalid Username or Password"), 401


app.register_blueprint(news_routes.news_routes)

if __name__ == '__main__':
    app.run(host="*", debug=True)
