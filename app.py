from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.utils import quote

import os, json, requests, psycopg2, psycopg2.extras

app = Flask(__name__)
cors = CORS(app)
secret_key = "leaverequestMashaf"

# mengimport seluruh routes yang berhubungan dengan data leave requests database
from src.routes.DataLeaveRequests import *

if __name__ == "__main__":
    app.run(debug=True)