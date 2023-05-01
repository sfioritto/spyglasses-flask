from functools import wraps
from flask import request, g, current_app, abort
from spyglasses.models import User, Token, db
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    unset_jwt_cookies,
)


def jwt_exempt(f):
    f._jwt_exempt = True
    return f


def invalidate_all_tokens_for_user(current_user_id):
    tokens = Token.query.filter_by(user_id=current_user_id).all()
    for token in tokens:
        token.is_revoked = True

    db.session.commit()


def load_current_user():
    try:
        # Check if the request is a preflight request
        # if you run verify_jwt_in_request() on a preflight request
        # it will return None and cause the request to fail
        if request.method == 'OPTIONS':
            return

        # Check if JWT exists and is valid
        verify_jwt_in_request()
        # Get the JWT's unique identifier
        jti = get_jwt()['jti']
        # Check if the token is revoked
        token = Token.query.filter_by(jti=jti).first()
        if not token or token.is_revoked:
            raise Exception('Token is revoked')

        # Get the current user's identity
        current_user_identity = get_jwt_identity()

        # Fetch the user from your database, e.g., using user ID or username
        current_user = User.query.get(current_user_identity)

        # Store the user in the 'g' object
        g.user = current_user
    except Exception as e:
        abort(401, description="Unauthorized")


def require_jwt_for_all_routes():
    # Get the current route function
    route_func = current_app.view_functions.get(request.endpoint)

    if route_func and not getattr(route_func, '_jwt_exempt', False):
        @wraps(require_jwt_for_all_routes)
        def wrapper():
            pass

        jwt_required()(wrapper)()
