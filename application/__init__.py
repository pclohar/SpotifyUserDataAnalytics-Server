from flask import Flask
from flask_cors import CORS
import os

def create_app():
    # create and configure the app
    flaskApp = Flask(__name__, instance_relative_config=True)
    CORS(flaskApp)
    flaskApp.config.from_mapping(
        SECRET_KEY = b';y\xd3\xd3\xe5\xa6\x119(&;Ea\x17\xfe\xdc'
    )

    

    try:
        os.makedirs(flaskApp.instance_path)
    except OSError:
        pass

    from . import auth
    flaskApp.register_blueprint(auth.bp)

    from . import songs
    flaskApp.register_blueprint(songs.bp)

    return flaskApp