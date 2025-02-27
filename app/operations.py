from app.utils import id_to_url, demo_id, id_to_resolver_link, hash
from app.services import AgentController, AskarStorage
import uuid
from config import Config

async def provision_demo():
    client_id = hash(str(uuid.uuid4()))
    askar = AskarStorage()
    agent = AgentController()
    invitation = agent.create_oob_connection(client_id)
    connection = agent.get_connection(client_id)
    connection_id = connection.get('connection_id')
    await askar.store(
            "exchange", connection_id, invitation["invitation"]
        )
    demo = await askar.fetch("demo", demo_id(Config.DEMO))
    demo = demo | {
        "schema_url": id_to_resolver_link(demo["schema_id"]),
        "cred_def_url": id_to_resolver_link(demo["cred_def_id"]),
        "rev_def_url": id_to_resolver_link(demo["rev_def_id"]),
    }
    invitation["short_url"] = (
        f"{Config.ENDPOINT}/exchange/{connection_id}"
    )
    return client_id, invitation, demo

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
    