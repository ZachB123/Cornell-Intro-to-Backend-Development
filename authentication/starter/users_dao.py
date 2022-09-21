"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from db import User


def get_user_by_email(email):
    """
    Returns a user object from the database given an email
    """
    return User.query.filter(User.email == email).first()


def get_user_by_session_token(session_token):
    """
    Returns a user object from the database given a session token
    """
    return User.query.filter(User.session_token == session_token).first()


def get_user_by_update_token(update_token):
    """
    Returns a user object from the database given an update token
    """
    return User.query.filter(User.update_token == update_token).first()


def verify_credentials(email, password):
    """
    Returns true if the credentials match, otherwise returns false
    """
    pass


def create_user(email, password):
    """
    Creates a User object in the database

    Returns if creation was successful, and the User object
    """
    pass


def renew_session(update_token):
    """
    Renews a user's session token
    
    Returns the User object
    """
    pass
