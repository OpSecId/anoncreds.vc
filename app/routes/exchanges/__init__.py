from flask import Blueprint, render_template, url_for, current_app, session, redirect, jsonify
import time
from asyncio import run as await_
from app.services import AgentController, AskarStorage

bp = Blueprint("exchanges", __name__)


@bp.before_request
def before_request_callback():
    if "demo" not in session:
        return {}, 401

@bp.route("/exchanges/<exchange_id>")
def exchanges(exchange_id: str):
    exchange = await_(AskarStorage().fetch('exchange', exchange_id))
    if not exchange:
        return {}, 404
    return exchange

@bp.route("/offer")
def credential_offer():
    agent = AgentController()
    try:
        session["demo"]["pres_ex_id"] = 'deleted'
        connection = agent.get_connection(session.get('demo').get("instance_id"))
        session["demo"]["cred_ex_id"] = agent.send_offer(
            connection.get("connection_id"),
            session["demo"].get("cred_def_id"),
            session["demo"].get("preview"),
        ).get("cred_ex_id")
    except:
        pass
    return redirect(url_for("index"))

@bp.route("/update")
def credential_update():
    agent = AgentController()
    try:
        session["demo"]["pres_ex_id"] = 'deleted'
        agent.revoke_credential(session["demo"].get("cred_ex_id"))
    except:
        pass
    return redirect(url_for("index"))

@bp.route("/request")
def presentation_request():
    agent = AgentController()
    try:
        connection = agent.get_connection(session.get('demo').get("instance_id"))
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

@bp.route("/message")
def send_message():
    AgentController().send_joke(session.get("demo").get("connection").get("connection_id"))
    return redirect(url_for("index"))