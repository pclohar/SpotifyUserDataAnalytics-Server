import functools
from flask_cors import cross_origin
import requests
from urllib.parse import quote
from flask import (
    Blueprint, request, session, json, jsonify, make_response
)
from application.common import get_response, make_request


bp = Blueprint('songs', __name__, url_prefix='/songs')

USER_TOP_SONGS_URL = 'https://api.spotify.com/v1/me/top/tracks'
USER_RECENTLY_PLAYED = 'https://api.spotify.com/v1/me/player/recently-played'

user_top_songs_parameters = {
    "time_range": "long_term"
}
user_recent_songs_parameters ={
    "type" : "track",
    "limit" : "50"
}

@bp.route("/top",methods=["GET"])
@cross_origin()
def get_top_songs():
    print("reached get_top_songs")
    endpoint = make_request(user_top_songs_parameters, USER_TOP_SONGS_URL)
    print("Endpoint :", endpoint)
    top_songs_response = get_response(endpoint)
    print("access token :",session['access_token'])
    res = json.loads(top_songs_response.text)
    res = make_response(jsonify(res['items']), 200)

    return res


@bp.route("/recent",methods=["GET"])
@cross_origin()
def get_recent_songs():

    endpoint = make_request(user_recent_songs_parameters, USER_RECENTLY_PLAYED)
    recent_songs_response = get_response(endpoint)

    res = json.loads(recent_songs_response.text)
    res = make_response(jsonify(res['items']), 200)

    return res