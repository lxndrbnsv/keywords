import os

from flask import request, send_file, jsonify

from app import app, db
from app.models import KeywordsDomain


@app.route("/")
@app.route("/index")
def index():
    return jsonify(status=None)


@app.route("/get_keywords_by_domain/<domain>")
def get_keywords_by_domain(domain):
    return jsonify(results=None)


@app.route("/send_file/<file_name>")
def send_file(file_name):
    return jsonify(status=None)
