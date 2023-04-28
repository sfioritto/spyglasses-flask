import requests
from flask import Blueprint, request, g, Response
from newspaper import Article
from spyglasses.models import Post, db

bp = Blueprint("views", __name__)
