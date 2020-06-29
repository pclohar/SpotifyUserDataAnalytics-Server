import functools
import requests
from urllib.parse import quote
from flask import (
    Blueprint, request, session, json, jsonify, make_response
)
from application.config import config

def get_auth_header(token):
    return {"Authorization": "Bearer {}".format(token)}


def make_request(query_parameters, url):
    url_args = "&".join(["{}={}".format(key, quote(val))
                         for key, val in query_parameters.items()])

    endpoint = "{}?{}".format(url, url_args)
    return endpoint

def get_response(endpoint):
    response = requests.get(
        endpoint, headers=get_auth_header(request.cookies.get('access_token'))
    )

    return response