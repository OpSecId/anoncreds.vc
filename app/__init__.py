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

    @app.route("/")
    def index():
        session['client_id'] = str(uuid.uuid4())
        session['demo'] = asyncio.run(AskarStorage().fetch('demo', 'default'))
        return render_template('pages/index.jinja')

    @app.route("/offer")
    def credential_offer():
        cred_ex_id, invitation = AgentController().offer_credential(
            session['client_id'],
            session['demo'].get('cred_def_id'),
            {
                'attributeClaim': 'Hello World',
                'predicateClaim': '2025'
            }
        )
        asyncio.run(AskarStorage().store('exchanges', cred_ex_id, invitation))
        session['cred_ex_id'] = cred_ex_id
        session['offer_ex_url'] = f'{Config.ENDPOINT}/exchanges/{cred_ex_id}'
        return render_template('pages/offer.jinja')

    @app.route("/request")
    def presentation_request():
        pres_ex_id, invitation = AgentController().request_presentation(
            'Demo Presentation',
            session['demo'].get('cred_def_id'),
            ['attributeClaim']
        )
        asyncio.run(AskarStorage().store('exchanges', pres_ex_id, invitation))
        session['pres_ex_id'] = pres_ex_id
        session['pres_ex_url'] = f'{Config.ENDPOINT}/exchanges/{pres_ex_id}'
        return render_template('pages/request.jinja')

    @app.route("/exchanges/<exchange_id>")
    def exchanges(exchange_id: str):
        invitation = asyncio.run(AskarStorage().fetch('exchanges', exchange_id))
        if invitation:
            return invitation
        return {}, 404

    @app.route("/verify")
    def verify_presentation():
        verified = AgentController().verify_presentation(session['pres_ex_id'])
        verified = True if verified.get('verified') else False
        return render_template('pages/verify.jinja', verified=verified)

    return app
