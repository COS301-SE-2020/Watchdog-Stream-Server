from flask import Flask
from manager import build
from flask import request
from flask import jsonify
import asyncio


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "200"

    @app.route('/offer', methods=['POST'])
    def offer():
        data = request.get_json()
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop = asyncio.get_event_loop()
        # tasks = manager.connect_camera(data['camera_id'], data['sdp'], data['type'])
        # response = loop.run_until_complete(asyncio.gather(*tasks))
        # loop.close()
        response = manager.connect_camera(data['camera_id'], data['sdp'], data['type'])
        print(response)
        if response is not None:
            return jsonify(response)
        else:
            return jsonify({})

    manager = build(app)

    return app
