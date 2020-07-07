import functools
import requests
from urllib.parse import quote
from flask_cors import cross_origin
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, json, jsonify, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash

from application.config import config

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
REDIRECT_URI = "http://localhost:3000/login"
SCOPE = "user-read-recently-played user-top-read user-read-email user-read-private"

USER_TOP_SONGS_URL = 'https://api.spotify.com/v1/me/top/tracks'
USER_RECENTLY_PLAYED = 'https://api.spotify.com/v1/me/player/recently-played'

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": config['client_id']
}

user_top_songs_parameters = {
    "time_range": "long_term"
}
user_recent_songs_parameters ={
    "type" : "track",
    "limit" : "50"
}
def get_auth_header(token):
    return {"Authorization": "Bearer {}".format(token)}


def auth_payload(token):
    return {
        "grant_type": "authorization_code",
        "code": str(token),
        "redirect_uri": REDIRECT_URI,
        "client_id": config['client_id'],
        "client_secret": config['client_secret'],
    }

def get_user_profile(token):
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(
        user_profile_api_endpoint, headers=get_auth_header(token)
    )

    return json.loads(profile_response.text)


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

@bp.route("/redirect-spotify")
@cross_origin()
def index():
    url_args = "&".join(["{}={}".format(key, quote(val))
                         for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return auth_url


@bp.route('/user', methods=('GET', 'POST'))
@cross_origin()
def get_user():
    access_token = ''

    if request.method == 'POST':
        data = request.json
        auth_token = data['code']
        print('Auth Token : ', auth_token)
        post_request = requests.post(SPOTIFY_TOKEN_URL, data=auth_payload(auth_token))
        
        response_data = json.loads(post_request.text)
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]

        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

    elif 'access_token' in session:
        access_token = session['access_token']

    profile_data = get_user_profile(access_token)

    if 'error' in profile_data:
        return 'Not logged in'
      
    session['user_id'] = profile_data['id']
    
    res = make_response(jsonify(profile_data), 200)
    res.set_cookie('access_token', access_token)

    return res

@bp.route('/logout')
@cross_origin()
def logout():
    session.clear()
    return 'True'

@bp.route("/top",methods=["GET"])
@cross_origin()
def get_top_songs():
    if request.method == 'GET':
        print("reached get_top_songs")
        endpoint = make_request(user_top_songs_parameters, USER_TOP_SONGS_URL)
        print("Endpoint :", endpoint)
        top_songs_response = get_response(endpoint)
        print("access token :",request.cookies.get('access_token'))
        res = json.loads(top_songs_response.text)
        res = make_response(jsonify(res['items']), 200)

        return res


@bp.route("/recent",methods=['GET'])
@cross_origin()
def get_recent_songs():
    if request.method == 'GET':
        endpoint = make_request(user_recent_songs_parameters, USER_RECENTLY_PLAYED)
        recent_songs_response = get_response(endpoint)

        res = json.loads(recent_songs_response.text)
        res = make_response(jsonify(res['items']), 200)

        return res