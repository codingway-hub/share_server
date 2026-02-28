from flask import Flask, send_file, request
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

@app.route('/')
def index():
    return "Hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
