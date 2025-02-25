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
from app.utils import id_to_url, demo_id, hash, fetch_resource, id_to_resolver_link
from app.operations import sync_demo


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    Session(app)
    Avatars(app)

    @app.before_request
    def before_request_callback():
        session["title"] = Config.APP_TITLE
        session["endpoint"] = Config.ENDPOINT
        session["agent"] = {
            "label": Config.DEMO.get("issuer"),
            "endpoint": Config.AGENT_ADMIN_ENDPOINT,
        }
        if "client_id" not in session:
            session["client_id"] = hash(str(uuid.uuid4()))
            demo = asyncio.run(AskarStorage().fetch("demo", demo_id(Config.DEMO)))
            session["demo"] = demo | {
                "schema_url": id_to_resolver_link(demo["schema_id"]),
                "cred_def_url": id_to_resolver_link(demo["cred_def_id"]),
                "rev_def_url": id_to_resolver_link(demo["rev_def_id"]),
            }

            agent = AgentController()
            session["invitation"] = agent.create_oob_connection(session["client_id"])
            oob_id = session["invitation"]["oob_id"]
            asyncio.run(
                AskarStorage().store(
                    "invitation", oob_id, session["invitation"]["invitation"]
                )
            )
            session["invitation"]["short_url"] = (
                f"{Config.ENDPOINT}/invitation/{oob_id}"
            )

    @app.route("/")
    def index():
        agent = AgentController()
        session["demo"] = sync_demo(session["demo"])
        session["connection"] = agent.get_connection(session["client_id"])
        session["connection"]["hash"] = hash(
            session["connection"].get("their_label")
            or session["connection"].get("connection_id")
        )
        session["status_list"] = agent.get_status_list(session["demo"]["rev_def_id"])
        return render_template(
            "pages/index.jinja", demo=session["demo"], status=session["status_list"]
        )

    @app.route("/restart")
    def restart():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/offer")
    def credential_offer():
        agent = AgentController()
        try:
            connection = agent.get_connection(session.get("client_id"))
            session["demo"]["cred_ex_id"] = agent.send_offer(
                connection.get("connection_id"),
                session["demo"].get("cred_def_id"),
                session["demo"].get("preview"),
            ).get("cred_ex_id")
            session["demo"]["presentation"] = {}
            session["demo"].pop("pres_ex_id", None)
        except:
            pass
        return redirect(url_for("index"))

    @app.route("/update")
    def credential_update():
        agent = AgentController()
        try:
            AgentController().revoke_credential(session["demo"].get("cred_ex_id"))
            session["demo"]["presentation"] = {}
            session["demo"].pop("pres_ex_id", None)
        except:
            pass
        return redirect(url_for("index"))

    @app.route("/request")
    def presentation_request():
        agent = AgentController()
        try:
            connection = agent.get_connection(session.get("client_id"))
            session["demo"]["pres_ex_id"] = agent.send_request(
                connection.get("connection_id"),
                "Demo Presentation",
                session["demo"].get("cred_def_id"),
                session["demo"].get("request").get("attributes"),
                session["demo"].get("request").get("predicate"),
                int(time.time()),
            ).get("pres_ex_id")
        except:
            pass
        return redirect(url_for("index"))

    @app.route("/resource", methods=["GET", "POST"])
    def render_resource():
        resource_id = request.args.get('id')
        try:
            resource = fetch_resource(resource_id)
            resource_url = id_to_url(resource_id)
            return render_template("pages/resource.jinja", resource=resource, resource_url=resource_url)
        except:
            return {}, 404

    @app.route("/joke")
    def send_joke():
        AgentController().send_joke(session.get("connection").get("connection_id"))
        return redirect(url_for("index"))

    @app.route("/invitation/<oob_id>")
    def exchanges(oob_id: str):
        invitation = asyncio.run(AskarStorage().fetch("invitation", oob_id))
        if not invitation:
            return {}, 404
        return invitation

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
