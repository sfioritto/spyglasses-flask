import requests
from flask import Blueprint, request, g, Response
from newspaper import Article
from spyglasses.models import Post, db

bp = Blueprint("views", __name__)


@bp.route('/', defaults={'path': ''}, methods=['GET'])
@bp.route('/<path:path>', methods=['GET'])
def proxy(path):
    url = f"https://{path}"
    headers = {key: value for key, value in request.headers if key != 'Host'}
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    try:
        # Parse the article using newspaper3k
        article_html = response.content
        article = Article('')
        article.set_html(article_html)
        article.parse()
        if article.is_valid_body():
            # Create a new Post instance with the parsed data
            post = Post(
                blurb=article.title,
                content=article.text,
                type='external',
                url=url,
                user=g.user
            )

            # Save the Post instance to the database
            db.session.add(post)
            db.session.commit()

    except Exception as error:
        print(f"An error occurred: {error}")

    proxy_response = Response(
        response.content, response.status_code, response.headers.items())

    return proxy_response
