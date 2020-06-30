from application import create_app


app = create_app()

@app.route('/')
def index():
    return "<h1>Welcome to our Flask Backend ... </h1>"

if __name__ == "__main__":
    app.run()