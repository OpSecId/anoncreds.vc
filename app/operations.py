from app.utils import id_to_url, id_to_resolver_link
from app.services import AgentController

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
    