from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import bedavnlp as rk
import traceback as tb

import subprocess

# if you want to download the large model
# subprocess.call("python -m spacy download en_core_web_lg",shell=True)
# subprocess.call("python -m spacy download en_core_web_sm",shell=True)

app = Flask(__name__)
CORS(app)

# if you want to load the large model
# nlp = spacy.load("en_core_web_lg")
# nlp = spacy.load("en_core_web_sm")
# print("Loaded language model")

@app.route('/process-bc7wnbd8', methods=['POST'])
@cross_origin()
def get_keywords():
    try:
        query_string = request.json.get("query")
        print("Query string in json:", query_string)
        if query_string is None: return
    except:
        query_string = request.form["query"]
        if query_string is None: return
    try:
        data = rk.process_sentence(query_string)
    except Exception as e:
        print(e)
        tb.print_exc()
        data = {"error":"could not process","error details":str(e)}
    return jsonify(data)
@app.route('/process-bc7wnbd8', methods=['GET'])
def return_get_request():
    return jsonify({"hello":"hi please use post!"})
# @app.route('/api/fuzzy-matches', methods=['POST'])
# def get_fuzzy_matches():
#     token = request.json.get("token")
#     dictionary = request.json.get("dictionary")
#     similar_words = get_fuzzy_similarity(token,dictionary)
#     return jsonify(similar_words = similar_words)
