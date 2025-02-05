from flask import Flask, render_template, session
from flask_cors import CORS
from flask_qrcode import QRcode
from flask_session import Session
from config import Config
import asyncio
import uuid
from app.services import AskarStorage, AgentController
from app.utils import id_to_url


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    Session(app)

    @app.before_request
    def before_request_callback():
        session['endpoint'] = Config.ENDPOINT
        if not session.get('client_id'):
            client_id = session['client_id'] = str(uuid.uuid4())
            invitation = AgentController().create_oob_connection(client_id)
            asyncio.run(AskarStorage().store('exchanges', client_id, invitation['invitation']))
            session['invitation'] = f'{Config.ENDPOINT}/exchanges/{client_id}'
            session['connection'] = AgentController().get_connection_id(client_id)
        if not session.get('demo'):
            session['demo'] = asyncio.run(AskarStorage().fetch('demo', 'default'))

    @app.route("/")
    def index():
        return render_template('pages/index.jinja')

    @app.route("/offer")
    def credential_offer(client_id: str):
        if client_id != session.get('client_id'):
            return {}, 400
        connection_id = AgentController().get_connection_id(client_id)
        cred_ex_id, invitation = AgentController().send_offer(
            connection_id,
            session['client_id'],
            session['demo'].get('cred_def_id'),
            {
                'attributeClaim': 'Hello World',
                'predicateClaim': '2025'
            }
        )

    @app.route("/request")
    def presentation_request(client_id: str):
        if client_id != session.get('client_id'):
            return {}, 400
        connection_id = AgentController().get_connection_id(client_id)
        pres_ex_id, invitation = AgentController().send_request(
            connection_id,
            'Demo Presentation',
            session['demo'].get('cred_def_id'),
            ['attributeClaim']
        )

    @app.route("/exchanges/<client_id>")
    def exchanges(client_id: str):
        invitation = asyncio.run(AskarStorage().fetch('exchanges', client_id))
        if invitation:
            return invitation
        return {}, 404

    @app.route("/verify")
    def verify_presentation():
        verified = AgentController().verify_presentation(session['pres_ex_id'])
        verified = True if verified.get('verified') else False
        return render_template('pages/verify.jinja', verified=verified)

    return app
