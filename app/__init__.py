from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_qrcode import QRcode
from flask_session import Session
from flask_avatars import Avatars
from config import Config
import asyncio
import uuid
from app.routes.exchanges import bp as exchanges_bp
from app.routes.webhooks import bp as webhooks_bp
from app.services import AskarStorage, AgentController
from app.utils import id_to_url, demo_id, hash, fetch_resource, id_to_resolver_link
from app.operations import provision_demo, sync_connection, sync_demo, update_chat


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    Session(app)
    Avatars(app)
    
    app.register_blueprint(exchanges_bp)
    app.register_blueprint(webhooks_bp)

    @app.before_request
    def before_request_callback():
        session["title"] = Config.APP_TITLE
        session["endpoint"] = Config.ENDPOINT
        session["agent"] = {
            "label": Config.DEMO.get("issuer"),
            "endpoint": Config.AGENT_ADMIN_ENDPOINT,
        }
        if "client_id" not in session:
            (session["client_id"], 
             session["invitation"], 
             session["demo"]) = asyncio.run(provision_demo())

    @app.route("/")
    def index():
        print(session['client_id'])
        agent = AgentController()
        session["demo"] = sync_demo(session["demo"])
        session["connection"] = sync_connection(session["client_id"])
        session["status_list"] = agent.get_status_list(session["demo"]["rev_def_id"])
        session["demo"]['chat_log'] = update_chat(session["connection"].get("connection_id"))
        return render_template(
            "pages/index.jinja", demo=session["demo"], status=session["status_list"]
        )

    @app.route("/restart")
    def restart():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/sync")
    def sync_state():
        if not session.get('client_id'):
            return {}, 401
        agent = AgentController()
        demo = session['demo']
        session['state'] = {}
        # demo = sync_demo(session["demo"])
        client_id = session['client_id']
        cred_ex_id = demo.get('cred_ex_id')
        pres_ex_id = demo.get('pres_ex_id')
        session['state']['connection'] = agent.get_connection(client_id)
        session['state']['cred_ex'] = agent.verify_offer(cred_ex_id) if cred_ex_id else {}
        session['state']['pres_ex'] = agent.verify_presentation(pres_ex_id) if pres_ex_id else {}
        print(session['state']['connection'].get('alias'))
        print(session['state']['connection'].get('state'))
        print(session['state']['cred_ex'].get('state'))
        print(session['state']['pres_ex'].get('state'))
        # chat = update_chat(session["connection"].get("connection_id"))
        return {
            'connection': session.get('connection'),
            'client_id': session.get('client_id'),
            # 'chat_log': chat
        }, 200

    @app.route("/resource", methods=["GET", "POST"])
    def render_resource():
        resource_id = request.args.get('id')
        try:
            resource = fetch_resource(resource_id)
            resource_url = id_to_url(resource_id)
            return render_template("pages/resource.jinja", resource=resource, resource_url=resource_url)
        except:
            return {}, 404

    return app
