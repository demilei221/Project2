from flask import Flask
from flask_cors import CORS
import json

import main

app = Flask(__name__)
# CORS(app)


@app.route("/")
def home():
    return "Hi"



@app.route("/<address>/<county>/<state>/<zip_code>/<business_type>")
def info(address, county, state, zip_code, business_type):
    # print(main.get_info(address, county, state, zip_code, business_type))
    return json.dumps(main.get_info(address, county.title(), state.title(), zip_code, business_type))

@app.route('/<state>')
def getCounties(state):
    return json.dumps(main.getCounties(state))


@app.route("/States")
def getStates():
    return  json.dumps(main.getStates())

app.run()