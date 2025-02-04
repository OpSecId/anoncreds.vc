from flask import Flask, render_template, session
from flask_cors import CORS
from flask_qrcode import QRcode
from flask_session import Session
from config import Config
import asyncio
from app.services import AskarStorage, AgentController
from app.utils import id_to_url


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    Session(app)

    @app.route("/")
    def index():
        session['demo'] = asyncio.run(AskarStorage().fetch('demo', 'default'))
        return render_template(
            'pages/index.jinja'
        )

    @app.route("/offer")
    def credential_offer():
        session['offer_ex_url'] = ''
        return render_template()

    @app.route("/request")
    def presentation_request():
        session['pres_ex_url'] = ''
        return render_template()

    @app.route("/exchanges/<exchange_id>")
    def exchanges(exchange_id: str):
        return render_template()

    return app
