
from datetime import datetime

from app.utils import query_from_issuer_id, query_from_resource_id
from app.services import AgentController, AskarStorage


agent = AgentController()
askar = AskarStorage()


def setup_demo():
    agent.configure_plugin()

    issuer_id = agent.create_did().get("state").get("id")

    schema_id = agent.create_schema(issuer_id).get("schema_state").get("schema_id")

    cred_def_id = (
        agent.create_cred_def(schema_id)
        .get("credential_definition_state")
        .get("credential_definition_id")
    )

    rev_reg_id = (
        agent.get_active_registry(cred_def_id).get("result").get("revoc_reg_id")
    )

    return {
        "issuer_id": issuer_id,
        "issuer_query": query_from_issuer_id(issuer_id),
        "schema_id": schema_id,
        "schema_query": query_from_resource_id(schema_id),
        "cred_def_id": cred_def_id,
        "cred_def_query": query_from_resource_id(cred_def_id),
        "rev_reg_id": rev_reg_id,
        "rev_reg_query": query_from_resource_id(rev_reg_id),
    }


def new_connection():
    invitation = agent.create_invitation()
    connection = agent.find_connection(invitation.get("invi_msg_id")).get("results")[0]
    oob_id = invitation.get("oob_id")
    return {
        # 'oob_id': oob_id,
        # 'short_url': f'{Config.ENDPOINT}/invitations/{oob_id}',
        "connection_id": connection.get("connection_id"),
        "connection_state": connection.get("state"),
        "invitation_url": invitation.get("invitation_url"),
        # 'invitation': invitation.get('invitation'),
    }


def new_issuance(connection_id, cred_def_id):
    cred_ex_id = agent.send_credential_offer(connection_id, cred_def_id).get(
        "cred_ex_id"
    )
    credential_exchange = agent.get_credential_exchange(cred_ex_id)
    return {
        "issuance_id": cred_ex_id,
        "issuance_state": credential_exchange.get("cred_ex_record").get("state"),
    }


def new_presentation(connection_id, cred_def_id):
    pres_ex_id = agent.send_presentation_request(
        connection_id, cred_def_id, int(datetime.now().timestamp())
    ).get("pres_ex_id")
    presentation_exchange = agent.get_presentation_exchange(pres_ex_id)
    return {
        "presentation_id": pres_ex_id,
        "presentation_state": presentation_exchange.get("state"),
        "presentation_verified": presentation_exchange.get("verified"),
    }


# async def setup_tenant(session):
#     session_id = str(uuid.uuid4())
#     session['invitation_url'] = f'{Config.ENDPOINT}/invitations/{session_id}'
#     session['connection_id'] = session_id

#     wallet_info = agent.create_subwallet(session_id)
#     await askar.store('wallets', session_id, wallet_info)

#     session['token'] = wallet_info.get('token')
#     await agent.set_token(session['token'])

#     invitation = agent.create_invitation().get('invitation')
#     await askar.store('invitations', session_id, invitation)

#     connection = agent.find_connection(invitation.get('@id')).get('results')[0]
#     session['connection_id'] = connection.get('connection_id')

#     webvh_config = agent.get_did_webvh_configuration()
#     agent.configure_did_webvh(webvh_config.get('witness_invitation'))

#     issuer_id = agent.create_did(session_id).get('id')
#     schema = Config.SCHEMA | {'issuerId': issuer_id}
#     schema_id = agent.create_schema(schema).get('schema_state').get('schema_id')
#     # agent.create_cred_def(schema_id).get('schema_state').get('schema_id')

# async def provision_demo():
#     instance_id = hash(str(uuid.uuid4()))
#     invitation = agent.create_oob_connection(instance_id)
#     connection = agent.get_connection_from_alias(instance_id)
#     connection_id = connection.get('connection_id')
#     invitation["short_url"] = (
#         f"{Config.ENDPOINT}/exchanges?_oobid={connection_id}"
#     )

#     await askar.store(
#             "exchange", connection_id, invitation["invitation"]
#         )
#     demo = await askar.fetch("demo", demo_id(Config.DEMO))
#     demo["rev_def_id"] = agent.get_active_registry(demo["cred_def_id"])
#     demo = demo | {
#         "status_size": Config.DEMO.get('size'),
#         "invitation": invitation,
#         "connection": connection,
#         "instance_id": instance_id,
#         "schema_url": id_to_resolver_link(demo["schema_id"]),
#         "cred_def_url": id_to_resolver_link(demo["cred_def_id"]),
#         "rev_def_url": id_to_resolver_link(demo["rev_def_id"]),
#         "agent": {
#             "label": Config.DEMO.get("issuer"),
#             "endpoint": Config.AGENT_ADMIN_ENDPOINT,
#         }
#     }
#     return demo

# def sync_connection(client_id):
#     connection = agent.get_connection(client_id)
#     connection['hash'] = hash(
#         connection.get("their_label")
#         or connection.get("connection_id")
#     )
#     return connection

# async def sync_demo(connection_id):
#     demo = await askar.fetch('demo', connection_id)
#     cred_ex_id = await askar.fetch('cred_ex_id', connection_id)
#     pres_ex_id = await askar.fetch('pres_ex_id', connection_id)

#     demo['issuance'] = {}
#     demo['presentation'] = {}
#     demo['rev_def_id'] = agent.get_active_registry(demo['cred_def_id'])
#     demo['rev_def_url'] = id_to_resolver_link(demo['rev_def_id'])

#     if cred_ex_id:
#         offer = agent.verify_offer(demo.get('cred_ex_id'))
#         demo['issuance'] = {
#             'state': offer.get('state')
#         }
#     if pres_ex_id:
#         presentation = agent.verify_presentation(demo.get('pres_ex_id'))
#         demo['presentation'] = {
#             'state': presentation.get('state'),
#             'verified': presentation.get('verified')
#         }
#     return demo

# async def sync_demo_state(connection_id):
#     demo = await askar.fetch('demo', connection_id)

#     state = {}
#     state['connection'] = agent.get_connection(connection_id)
#     state['connection']['hash'] = hash(
#         state['connection'].get("their_label")
#         or connection_id
#     )

#     cred_ex_id = await askar.fetch('cred_ex_id', connection_id)
#     pres_ex_id = await askar.fetch('pres_ex_id', connection_id)
#     if cred_ex_id is None:
#         state['cred_ex'] = {'state': None}
#     elif cred_ex_id == 'deleted':
#         state['cred_ex'] = {'state': 'deleted'}
#     else:
#         state['cred_ex'] = agent.verify_offer(cred_ex_id)

#     if pres_ex_id is None:
#         state['pres_ex'] = {'state': None}
#     elif pres_ex_id == 'deleted':
#         state['pres_ex'] = {'state': 'deleted'}
#     else:
#         state['pres_ex'] = agent.verify_presentation(pres_ex_id)

#     status_list = agent.get_latest_sl(demo.get('cred_def_id'))
#     state['status_widget'] = {
#         'html': ''
#     }
#     for bit in status_list:
#         if bit == 0:
#             state['status_widget']['html'] += '<div class="tracking-block bg-success" data-bs-toggle="tooltip" data-bs-placement="top" title="ok"></div>\n'
#         elif bit == 1:
#             state['status_widget']['html'] += '<div class="tracking-block bg-danger" data-bs-toggle="tooltip" data-bs-placement="top" title="revoked"></div>\n'
#         else:
#             state['status_widget']['html'] += '<div class="tracking-block bg-warning" data-bs-toggle="tooltip" data-bs-placement="top" title="unknown"></div>\n'
#     return state

# def update_chat(connection_id):
#     chat_log = []
#     # chat_log.append({
#     #     'connection_id': connection_id,
#     #     'content': 'Hi',
#     #     'timestamp': '02-02-12T00:00:00Z',
#     #     'author_hash': hash('My label'),
#     #     'author': 'My label',
#     #     'state': 'sent',
#     # })
#     # chat_log.append({
#     #     'connection_id': connection_id,
#     #     'content': 'Hello',
#     #     'timestamp': '02-02-12T00:10:00Z',
#     #     'author_hash': hash('Their label'),
#     #     'author': 'Their label',
#     #     'state': 'recieved',
#     # })
#     return chat_log
