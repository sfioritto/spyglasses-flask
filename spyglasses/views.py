import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask import redirect, render_template, session, url_for, Blueprint, current_app


def load_current_user():
    # This will look at the token in the session cookie
    # and try to load the user from the database
    # if the token is valid otherwise it will
    # redirect the user to the login page
    pass


bp = Blueprint("views", __name__)

bp.before_request(load_current_user)


@bp.route("/login")
def login():
    return current_app.auth0.authorize_redirect(
        redirect_uri=url_for("views.callback", _external=True)
    )


@bp.route("/callback", methods=["GET", "POST"])
def callback():
    token = current_app.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@bp.route("/")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))
