from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    """Verify the username and password from the basic auth in certain requests.
        The certain requests is routing to those routes with decorator
        @basic_auth.login_required .
        So before calling the decorated function, this function is called to verify the authorization.

    Args:
        username (string): from basic auth from request
        password (string): from basic auth from request

    Returns:
        User
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    """called before reqeust the route decorated with @token_auth.login_required

    Args:
        token (string): From request
    """
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)