import flask

app = flask.Flask(__name__)

@app.route("/")
def init():
    # TODO: create basic web page
    return "<p>This is the backend API.</p>"

