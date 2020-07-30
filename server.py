from flask import Flask, jsonify, request, render_template, flash, url_for
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
import bcrypt
from datetime import datetime, date, timedelta
import isodate as iso
from bson import ObjectId
from flask.json import JSONEncoder
from werkzeug.routing import BaseConverter
from controllers import news_routes, user_activities
from validate_email import validate_email
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail

# Making a Connection with MongoClient
client = MongoClient("mongodb://localhost:27017/")
# database
db = client["iNews"]
# collection
user = db["User"]
app = Flask(__name__, instance_relative_config=True,
            template_folder='html_template')
# app.config.from_envvar('APP_CONFIG_FILE')
app.config.from_object('config.default')
jwt = JWTManager(app)
mail = Mail(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = "JWTSECRETCHECK"


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return iso.datetime_isoformat(o)
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super().default(o)


class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)


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

        user_info = dict(first_name=first_name, last_name=last_name,
                         email=email, password=hashpass,
                         createtedAt=datetime.now(),
                         confirmed_email=False)
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

    test = user.find_one({"email": email})
    if not test:
        return jsonify(message="Invalid Username or Password"), 401
    if not test['confirmed_email']:
        return jsonify(message="Please activate your account"), 401
    if bcrypt.hashpw(password.encode('utf-8'),
                     test['password']) == test['password'] and test:
        expires = timedelta(days=7)
        access_token = create_access_token(identity=email,
                                           expires_delta=expires)
        return jsonify(message="Login Succeeded!",
                       username=test["first_name"],
                       userid=test["_id"],
                       access_token=access_token), 201
    else:
        return jsonify(message="Invalid Username or Password"), 401


app.json_encoder = MongoJSONEncoder
app.url_map.converters['objectid'] = ObjectIdConverter
app.register_blueprint(news_routes.news_routes)
app.register_blueprint(user_activities.user_activity)

if __name__ == '__main__':
    app.run(host="*", debug=True, port=5000)
