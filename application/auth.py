import functools
import requests
import datetime
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
REDIRECT_URI = "https://spotify-music-analytics.herokuapp.com/login"
SCOPE = "user-read-recently-played user-top-read user-read-email user-read-private"


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": config['client_id']
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
        req_text = post_request.text
        if "error" in req_text:
            return req_text["error_description"]

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
    res.set_cookie('access_token', access_token, expires=datetime.datetime.now() + datetime.timedelta(days=30))

    return res

@bp.route('/logout')
@cross_origin()
def logout():
    session.clear()
    return 'True'
