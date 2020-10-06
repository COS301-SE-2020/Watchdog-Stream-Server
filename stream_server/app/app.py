from flask import Flask
from .main.events import build
from flask import request
from flask import jsonify

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "200"

    @app.route('/offer', methods=['POST'])
    def offer():
        sid = request.sid
        data = request.get_json()
        manager.connect_camera(sid, data['camera_id'], data['sdp'], data['type'])

    manager = build(app)

    return app
