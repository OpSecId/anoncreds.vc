from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_qrcode import QRcode
from flask_session import Session
from flask_avatars import Avatars
from config import Config
import asyncio
import uuid
import time
from app.services import AskarStorage, AgentController
from app.utils import id_to_url, demo_id, hash


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    Session(app)
    Avatars(app)

    @app.before_request
    def before_request_callback():
        session['title'] = Config.APP_TITLE
        session['endpoint'] = Config.ENDPOINT
        session['agent'] = {
            'label': Config.DEMO.get('issuer'),
            'endpoint': Config.AGENT_ADMIN_ENDPOINT
        }
        if 'client_id' not in session:
            session['client_id'] = hash(str(uuid.uuid4()))
            demo = asyncio.run(AskarStorage().fetch('demo', demo_id(Config.DEMO)))
            session['demo'] = demo | {
                'schema_url': id_to_url(demo['schema_id']),
                'cred_def_url': id_to_url(demo['cred_def_id']),
                'rev_def_url': id_to_url(demo['rev_def_id']),
            }
            
            agent = AgentController()
            session['invitation'] = agent.create_oob_connection(session['client_id'])

    @app.route("/")
    def index():
        print(session['client_id'])
        agent = AgentController()
        session['demo']['issuance'] = {}
        session['demo']['presentation'] = {}
        session['connection'] = agent.get_connection(session['client_id'])
        session['status_list'] = agent.get_status_list(session['demo']['rev_def_id'])
        if session.get('demo').get('cred_ex_id'):
            print(session.get('demo').get('cred_ex_id'))
            offer = agent.verify_offer(session['demo'].get('cred_ex_id'))
            session['demo']['issuance'] = {
                'state': offer.get('state')
            }
        if session.get('demo').get('pres_ex_id'):
            presentation = agent.verify_presentation(session['demo'].get('pres_ex_id'))
            session['demo']['presentation'] = {
                'state': presentation.get('state'),
                'verified': True if presentation.get('verified') else False
            }
        return render_template('pages/index.jinja', demo=session['demo'], status=session['status_list'])
    
    @app.route("/restart")
    def restart():
        session.clear()
        return redirect(url_for('index'))

    @app.route("/offer")
    def credential_offer():
        print('Offer')
        try:
            connection = AgentController().get_connection(session.get('client_id'))
            print(connection)
            cred_offer = AgentController().send_offer(
                connection.get('connection_id'),
                session['demo'].get('cred_def_id'),
                session['demo'].get('preview')
            )
            print(cred_offer)
            session['demo']['cred_ex_id'] = cred_offer.get('cred_ex_id')
        except:
            pass
        return redirect(url_for('index'))

    @app.route("/update")
    def credential_update():
        try:
            connection = AgentController().get_connection(session.get('client_id'))
        except:
            pass
        return redirect(url_for('index'))

    @app.route("/request")
    def presentation_request():
        try:
            connection = AgentController().get_connection(session.get('client_id'))
            pres_req = AgentController().send_request(
                connection.get('connection_id'),
                'Demo Presentation',
                session['demo'].get('cred_def_id'),
                session['demo'].get('request').get('attributes'),
                session['demo'].get('request').get('predicate'),
                int(time.time())
            )
            session['demo']['pres_ex_id'] = pres_req.get('pres_ex_id')
        except:
            pass
        return redirect(url_for('index'))

    @app.route("/resource", methods=["GET", "POST"])
    def render_resource():
        resource = {}
        return render_template(
            'pages/resource.jinja',
            resource=resource
        )
    @app.route("/joke")
    def send_joke():
        AgentController().send_joke(
            session.get('connection').get('connection_id')
        )
        return redirect(url_for('index'))

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
