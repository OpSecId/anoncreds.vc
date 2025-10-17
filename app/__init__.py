from flask import (
    Flask,
    current_app,
    render_template,
    session,
    redirect,
    url_for,
    request,
)
from flask_cors import CORS
from flask_qrcode import QRcode
from flask_session import Session
from flask_avatars import Avatars
from config import Config
from asyncio import run as await_
import uuid
import json
import time

# from app.routes.exchanges import bp as exchanges_bp
# from app.routes.webhooks import bp as webhooks_bp
from app.services import AskarStorage, AgentController
from app.utils import id_to_url, demo_id, hash, fetch_resource, id_to_resolver_link
from app.operations import new_connection, new_issuance, new_presentation

agent = AgentController()
askar = AskarStorage()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.template_filter("ctime")
    def ctime(s):
        return time.ctime(s)

    @app.template_filter("dereference")
    def dereference(s):
        return id_to_url(s)

    @app.template_filter("resolve")
    def id_resolver(s):
        return id_to_resolver_link(s)

    @app.template_filter("format_date")
    def format_date(date_value):
        """Format YYYYMMDD date string or integer to readable format"""
        if not date_value:
            return date_value
        
        # Convert to string if it's an integer
        if isinstance(date_value, int):
            date_string = str(date_value)
        else:
            date_string = date_value
            
        if len(date_string) != 8:
            return date_string
            
        try:
            year = date_string[:4]
            month = date_string[4:6]
            day = date_string[6:8]
            # Remove leading zeros from month and day
            month = str(int(month))
            day = str(int(day))
            return f"{month}/{day}/{year}"
        except:
            return date_string

    CORS(app)
    QRcode(app)
    Session(app)
    Avatars(app)

    # askar = AskarStorage()
    # agent = AgentController()

    # app.register_blueprint(exchanges_bp)
    # app.register_blueprint(webhooks_bp)

    @app.before_request
    def before_request_callback():
        if not session.get("demo"):
            session["demo"] = await_(askar.fetch("demo", "demo"))
        session["title"] = "AnonCreds VC Demo"

    @app.route("/")
    def index():
        return redirect(url_for("connection"))

    @app.route("/connection")
    def connection():
        if not session.get("demo", {}).get("connection_id"):
            session["demo"] |= new_connection()

        session["demo"]["connection_state"] = agent.get_connection(
            session["demo"]["connection_id"]
        ).get("state")
        print(session["demo"]["issuer_id"])

        return render_template("pages/wizard/connection.jinja")

    @app.route("/issuance")
    def issuance():
        if not session.get("demo", {}).get("issuance_id") or request.args.get(
            "new_offer"
        ):
            session["demo"] |= new_issuance(
                session["demo"]["connection_id"],
                session["demo"]["cred_def_id"],
            )
        session["demo"]["issuance_state"] = (
            agent.get_credential_exchange(session["demo"]["issuance_id"])
            .get("cred_ex_record")
            .get("state")
        )
        return render_template("pages/wizard/issuance.jinja")

    @app.route("/verification")
    def verification():
        if request.args.get("revocation"):
            agent.revoke_credential(session["demo"]["issuance_id"])
            session["demo"] |= new_presentation(
                session["demo"]["connection_id"], session["demo"]["cred_def_id"]
            )
        if not session.get("demo", {}).get("presentation_id") or request.args.get(
            "new_request"
        ):
            session["demo"] |= new_presentation(
                session["demo"]["connection_id"], session["demo"]["cred_def_id"]
            )

        presentation_exchange = agent.get_presentation_exchange(
            session["demo"]["presentation_id"]
        )
        session["demo"]["presentation_state"] = presentation_exchange.get("state")
        session["demo"]["presentation_verified"] = presentation_exchange.get("verified")

        return render_template("pages/wizard/verification.jinja")

    @app.route("/results")
    def results():
        return render_template("pages/wizard/results.jinja")

    @app.route("/invitations")
    @app.route("/invitations/<oob_id>")
    def get_invitation(oob_id):
        return await_(askar.fetch("invitations", oob_id)) or {}

    @app.route("/restart")
    def restart():
        session.clear()
        return redirect(url_for("index"))

    # @app.route("/sync")
    # def sync_state():
    #     if not session.get('connection_id'):
    #         return {}, 400
    #     state = await_(sync_demo_state(session.get('connection_id')))
    #     # current_app.logger.warning(state)
    #     return state, 200

    # @app.route("/resource", methods=["GET", "POST"])
    # def render_resource():
    #     resource_id = request.args.get('id')
    #     try:
    #         resource = fetch_resource(resource_id)
    #         resource_url = id_to_url(resource_id)
    #         return render_template("pages/resource.jinja", resource=resource, resource_url=resource_url)
    #     except:
    #         return {}, 404

    return app
