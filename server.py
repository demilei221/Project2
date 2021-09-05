from flask import Flask
from flask_cors import CORS

import main

app = Flask(__name__)
# CORS(app)


@app.route("/")
def home():
    return "Hi"

@app.route("/<check>")
def hello(check):
    print(check)
    return 'Hello, World!'

@app.route("/<address>/<county>/<state>/<zip_code>/<business_type>")
def info(address, county, state, zip_code, business_type):
    print(address, county, state, zip_code, business_type)
    return main.get_info(address, county, state, zip_code, business_type)

app.run()