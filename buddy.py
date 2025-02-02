import flask
from vector_database import VectorDB
from urllib.parse import unquote

app = flask.Flask(__name__)

database = VectorDB()

@app.route("/")
def init():
    # TODO: create basic index page
    return "<p>This is the backend API.</p>"

@app.route("/buddy/", methods=['GET'])
def buddy_suggestion():
    # TODO: add route to reduce sources/vector database to just a select files
    # 1. Parse the 'query' parameter
    query = flask.request.args.get('query')
    # 2. Decode the 'query' parameter
    decoded_query = unquote(query)

    print(f"Decoded query is {decoded_query}")

    # 3. Pass it into the vectorDB
    response = database.run_query(decoded_query)

    print(f"Sources received from database is: {response['sources']}")

    # this is what the response is formatted like
    context = {
        "text": response['text'],
        "sources": response['sources']
    }

    return flask.jsonify(**context), 201

@app.route("/sources/", methods=["POST"])
def change_pdf_sources():
    # valid source results are: "all", "primary", "protocols", "safety"
    pdf_source = flask.request.args.get('source')
    
    changed_successfully = database.change_source(pdf_source)

    # if there's an invalid instruction
    if changed_successfully == -1:
        return flask.jsonify({}), 400
    return flask.jsonify({}), 201
