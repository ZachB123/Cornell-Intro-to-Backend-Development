import json

from db import db, User
import users_dao as dao
from flask import Flask, request

db_filename = "auth.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"success": False, "error": message}), code


def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, json.dumps({"error": "missing auth header"})
    #replaces bearer with nothing to remove it from auth strip removes whitespace from front and back
    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, json.dumps("invalid auth header")
    return True, bearer_token


@app.route("/")
def hello_world():
    """
    Endpoint for printing Hello World!
    """
    return "Hello World!"


@app.route("/register/", methods=["POST"])
def register_account():
    """
    Endpoint for registering a new user
    """
    body = json.loads(request.data)
    email, password = body.get("email"), body.get("password")
    if email is None or password is None:
        return json.dumps({"error": "invalid name or password"}), 400
    
    optional_user = dao.get_user_by_email(email)
    if optional_user is not None:
        return json.dumps({"error": "user already exists"})
    
    #password is encrypted in constructor of User
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return json.dumps({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })


@app.route("/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    email, password = body.get("email"), body.get("password")
    if email is None or password is None:
        return json.dumps({"error": "invalid name or password"}), 400

    user = dao.get_user_by_email(email)

    success = user is not None and user.verify_password(password)
    if not success:
        return json.dumps({"error": "incorrect email or password"})
    return json.dumps({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })


@app.route("/session/", methods=["POST"])
def update_session():
    """
    Endpoint for updating a user's session
    """
    success, update_token = extract_token(request)
    if not success:
        return update_token
    
    user = dao.get_user_by_update_token(update_token)
    if user is None:
        return json.dumps({"error": f"invalid update token {update_token}"})
    
    user.renew_session()
    db.session.commit()
    return json.dumps({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })


@app.route("/secret/", methods=["GET"])
def secret_message():
    """
    Endpoint for verifying a session token and returning a secret message

    In your project, you will use the same logic for any endpoint that needs 
    authentication
    """
    success, session_token = extract_token(request)
    if not success:
        return session_token
    
    user = dao.get_user_by_session_token(session_token)
    
    if user is None or (not user.verify_session_token(session_token)):
        return json.dumps({"error": "invalid session token"})
    
    return json.dumps({"message": "secret password is 69420"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
