from application import create_app
from flask_session import Session

app = create_app()
sess = Session()
sess.init_app(app)

@app.route('/')
def index():
    return "<h1>Welcome to our Flask Backend ... </h1>"

if __name__ == "__main__":
    app.run()