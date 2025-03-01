from app.utils import id_to_url, demo_id, id_to_resolver_link, hash
from app.services import AgentController, AskarStorage
import uuid
from config import Config

async def provision_demo():
    instance_id = hash(str(uuid.uuid4()))
    askar = AskarStorage()
    agent = AgentController()
    invitation = agent.create_oob_connection(instance_id)
    connection = agent.get_connection(instance_id)
    connection_id = connection.get('connection_id')
    await askar.store(
            "exchange", connection_id, invitation["invitation"]
        )
    invitation["short_url"] = (
        f"{Config.ENDPOINT}/exchange/{connection_id}"
    )
    demo = await askar.fetch("demo", demo_id(Config.DEMO))
    demo = demo | {
        "status_size": Config.DEMO.get('size'),
        "invitation": invitation,
        "connection": connection,
        "instance_id": instance_id,
        "schema_url": id_to_resolver_link(demo["schema_id"]),
        "cred_def_url": id_to_resolver_link(demo["cred_def_id"]),
        "rev_def_url": id_to_resolver_link(demo["rev_def_id"]),
        "agent": {
            "label": Config.DEMO.get("issuer"),
            "endpoint": Config.AGENT_ADMIN_ENDPOINT,
        }
    }
    return demo

def sync_connection(client_id):
    agent = AgentController()
    connection = agent.get_connection(client_id)
    connection['hash'] = hash(
        connection.get("their_label")
        or connection.get("connection_id")
    )
    return connection

def sync_demo(demo):
    agent = AgentController()
    demo['issuance'] = {}
    demo['presentation'] = {}
    demo['rev_def_id'] = agent.get_active_registry(demo['cred_def_id'])
    demo['rev_def_url'] = id_to_resolver_link(demo['rev_def_id'])
    if demo.get('cred_ex_id'):
        print(demo.get('cred_ex_id'))
        offer = agent.verify_offer(demo.get('cred_ex_id'))
        demo['issuance'] = {
            'state': offer.get('state')
        }
    if demo.get('pres_ex_id'):
        presentation = agent.verify_presentation(demo.get('pres_ex_id'))
        demo['presentation'] = {
            'state': presentation.get('state'),
            'verified': presentation.get('verified')
        }
    return demo

def sync_demo_state(demo):
    agent = AgentController()
    state = {}
    instance_id = demo['instance_id']
    cred_ex_id = demo.get('cred_ex_id')
    pres_ex_id = demo.get('pres_ex_id')
    state['connection'] = agent.get_connection(instance_id)
    state['hash'] = hash(
        state['connection'].get("their_label")
        or state['connection'].get("connection_id")
    )
    state['cred_ex'] = agent.verify_offer(cred_ex_id) if cred_ex_id else {'state': None}
    state['pres_ex'] = agent.verify_presentation(pres_ex_id) if pres_ex_id else {'state': None}
    state['status_list'] = agent.get_latest_sl(demo.get('cred_def_id'))
    state['status_widget'] = ''
    for bit in state['status_list']:
        if bit == 0:
            state['status_widget'] += '<div class="tracking-block bg-success" data-bs-toggle="tooltip" data-bs-placement="top" title="ok"></div>\n'
        elif bit == 1:
            state['status_widget'] += '<div class="tracking-block bg-danger" data-bs-toggle="tooltip" data-bs-placement="top" title="revoked"></div>\n'
        else:
            state['status_widget'] += '<div class="tracking-block bg-warning" data-bs-toggle="tooltip" data-bs-placement="top" title="unknown"></div>\n'
    return state

def update_chat(connection_id):
    chat_log = []
    # chat_log.append({
    #     'connection_id': connection_id,
    #     'content': 'Hi',
    #     'timestamp': '02-02-12T00:00:00Z',
    #     'author_hash': hash('My label'),
    #     'author': 'My label',
    #     'state': 'sent',
    # })
    # chat_log.append({
    #     'connection_id': connection_id,
    #     'content': 'Hello',
    #     'timestamp': '02-02-12T00:10:00Z',
    #     'author_hash': hash('Their label'),
    #     'author': 'Their label',
    #     'state': 'recieved',
    # })
    return chat_log
    