import json
import requests
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask import redirect, render_template, session, url_for, Blueprint, current_app, abort, g
from spyglasses.models import User, db


bp = Blueprint("views", __name__)


def load_user():
    userinfo = session.get("user")
    if not userinfo:
        abort(401)
    auth0_user_id = userinfo["sub"]
    user = User.query.filter_by(auth_user_id=auth0_user_id).first()
    if not user:
        abort(401)
    g.user = user


@bp.route("/login")
def login():
    return current_app.auth0.authorize_redirect(
        redirect_uri=url_for("views.callback", _external=True)
    )


@bp.route("/callback", methods=["GET", "POST"])
def callback():
    token = current_app.auth0.authorize_access_token()
    access_token = token["access_token"]

    auth0_userinfo_url = f"https://{env.get('AUTH0_DOMAIN')}/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(auth0_userinfo_url, headers=headers)
    userinfo = userinfo_response.json()

    auth0_user_id = userinfo["sub"]
    user = User.query.filter_by(auth_user_id=auth0_user_id).first()

    if not user:
        # Create a new User instance if it doesn't exist
        user = User(
            auth_user_id=auth0_user_id,
            email=userinfo.get("email"),
            given_name=userinfo.get("given_name"),
            family_name=userinfo.get("family_name"),
        )
        db.session.add(user)
        db.session.commit()

    session["user"] = userinfo

    return redirect("/")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("views.home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@bp.route("/")
def home():
    userinfo = session.get("user")
    if not userinfo:
        user = None
    else:
        auth0_user_id = userinfo["sub"]
        user = User.query.filter_by(auth_user_id=auth0_user_id).first()
    return render_template("home.html", user=user, pretty=json.dumps(session.get('user'), indent=4))
