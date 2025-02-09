from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_qrcode import QRcode
from flask_session import Session
from config import Config
import asyncio
import uuid
import time
from app.services import AskarStorage, AgentController
from app.utils import id_to_url


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    # Session(app)

    @app.before_request
    def before_request_callback():
        session['endpoint'] = Config.ENDPOINT
        if 'client_id' not in session:
            session['client_id'] = str(uuid.uuid4())
            session['demo'] = asyncio.run(AskarStorage().fetch('demo', 'default'))
            
            agent = AgentController()
            # session['demo']['rev_def_id'] = agent.get_active_registry(session['demo']['cred_def_id'])
            # session['demo']['rev_def_url'] = id_to_url(session['demo']['rev_def_id'])
            session['invitation'] = agent.create_oob_connection(session['client_id'])

    @app.route("/")
    def index():
        print(session['client_id'])
        agent = AgentController()
        session['connection'] = agent.get_connection(session['client_id'])
        if session['connection'].get('state') != 'active':
            return render_template('pages/connection.jinja')
        return render_template('pages/index.jinja')
    
    @app.route("/restart")
    def restart():
        session.clear()
        return redirect(url_for('index'))

    @app.route("/offer")
    def credential_offer():
        client_id = request.args.get('client_id')
        print(client_id)
        try:
            connection = AgentController().get_connection(client_id)
            cred_offer = AgentController().send_offer(
                connection.get('connection_id'),
                session['demo'].get('cred_def_id'),
                {
                    'attributeClaim': 'Hello World',
                    'predicateClaim': '2025'
                }
            )
            print(cred_offer.get('cred_ex_id'))
            return {}, 201
        except:
            return {}, 404

    @app.route("/request")
    def presentation_request():
        client_id = request.args.get('client_id')
        try:
            connection = AgentController().get_connection(client_id)
            pres_req = AgentController().send_request(
                connection.get('connection_id'),
                'Demo Presentation',
                session['demo'].get('cred_def_id'),
                ['attributeClaim'],
                ['predicateClaim', '>=', 2025],
                int(time.time())
            )
            print(pres_req.get('pres_ex_id'))
            return {}, 201
        except:
            return {}, 404

    # @app.route("/exchanges/<client_id>")
    # def exchanges(client_id: str):
    #     invitation = asyncio.run(AskarStorage().fetch('exchanges', client_id))
    #     if not invitation:
    #         return {}, 404
    #     return invitation

    # @app.route("/verify")
    # def verify_presentation():
    #     verified = AgentController().verify_presentation(session['pres_ex_id'])
    #     verified = True if verified.get('verified') else False
    #     return render_template('pages/verify.jinja', verified=verified)

    return app
