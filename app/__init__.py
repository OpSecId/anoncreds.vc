from flask import Flask, render_template
from flask_cors import CORS
from flask_qrcode import QRcode
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)

    @app.route("/")
    def index():
        return render_template('pages/index.jinja')

    @app.route("/offer")
    def credential_offer():
        return render_template()

    @app.route("/request")
    def presentation_request():
        return render_template()

    @app.route("/exchanges/<exchange_id>")
    def exchanges(exchange_id: str):
        return render_template()

    return app
