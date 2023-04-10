from flask import jsonify, request, Blueprint

bp = Blueprint("views", __name__)


@bp.route('/', methods=['GET'])
def get_home():
    return 'Hello, World!'
