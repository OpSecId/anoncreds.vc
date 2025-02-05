import os
import uuid
import requests
from app.services import AskarStorage
from app.utils import id_to_url
from config import Config
from random import randint


class AgentControllerError(Exception):
    """Generic AgentControllerError Error."""

class AgentController:
    def __init__(self):
        self.label = "AnonCreds Demo"
        self.namespace = "demo"
        self.identifier = str(uuid.uuid4())
        self.issuer = None
        self.webvh_server = os.getenv('DIDWEBVH_SERVER')
        self.did_web = f'did:web:{self.webvh_server.split("://")[-1]}:{self.namespace}:{self.identifier}'
        self.did_webvh = None
        self.witness_key = os.getenv('DIDWEBVH_WITNESS_KEY')
        self.endpoint = os.getenv('AGENT_ADMIN_ENDPOINT')
        # self.headers = {
        #     'X-API-KEY': os.getenv('AGENT_ADMIN_API_KEY')
        # }
        
    async def provision(self):
        await AskarStorage().update('demo', 'default', {})
        print('Configuring webvh')
        r = requests.post(
            f'{self.endpoint}/did/webvh/configuration',
            # headers=self.headers,
            json={
                'server_url': self.webvh_server,
                'witness_key': self.witness_key,
                'witness': True
            }
        )
        print(r.text)
        self.create_did_webvh(self.namespace, self.identifier)
        print('Resolving DID')
        try:
            r = requests.get(
                f'{self.endpoint}/resolver/resolve/{self.did_web}',
                # headers=self.headers,
            )
            print(self.did_web)
            # print(r.text)
            self.did_webvh = r.json()['did_document']['alsoKnownAs'][0]
        except:
            pass
        await self.setup_anoncreds()
        
    def create_did_webvh(self, namespace, identifier):
        print('Creating DID')
        try:
            r = requests.post(
                f'{self.endpoint}/did/webvh/create',
                # headers=self.headers,
                json={
                    'options': {
                        'identifier': identifier,
                        'namespace': namespace,
                        'parameters': {
                            'portable': False,
                            'prerotation': False
                        }
                    }
                }
            )
            print(r.text)
        except:
            pass
        
    async def setup_anoncreds(self):
        print('Setting up AnonCreds Demo')
        demo = await AskarStorage().fetch('demo', 'default')
        if demo:
            print('Demo already set')
            return
            
        options = {
            'verificationMethod': f'{self.did_webvh}#key-01',
            'serviceEndpoint': f'{self.webvh_server}/resources'
        }
        issuer_id = self.did_webvh
        schema_name = 'Demo Credential'
        schema_version = '1.0'
        schema_attributes = ['attributeClaim', 'predicateClaim']
        cred_def_tag = f'{schema_name}-def'
        rev_def_tag = f'{schema_name}-rev'
        revocation=True
        revocation_max=8
        try:
            print('Schema')
            r = requests.post(
                f'{self.endpoint}/anoncreds/schema',
                # headers=self.headers,
                json={
                    'options': options,
                    'schema': {
                        'attrNames': schema_attributes,
                        'issuerId': issuer_id,
                        'name': schema_name,
                        'version': schema_version
                    }
                }
            )
            schema_id = r.json()['schema_state']['schema_id']
        except:
            pass
        
        try:
            print('Credential Definition')
            r = requests.post(
                f'{self.endpoint}/anoncreds/credential-definition',
                # headers=self.headers,
                json={
                    'options': options | {'support_revocation': revocation},
                    'credential_definition': {
                        'issuerId': issuer_id,
                        'schemaId': schema_id,
                        'tag': cred_def_tag,
                    }
                }
            )
            cred_def_id = r.json()['credential_definition_state']['credential_definition_id']
        except:
            pass
        try:
            print('Revocation Registry')
            r = requests.post(
                f'{self.endpoint}/anoncreds/revocation-registry-definition',
                # headers=self.headers,
                json={
                    'options': options,
                    'revocation_registry_definition': {
                        'credDefId': cred_def_id,
                        'issuerId': issuer_id,
                        'maxCredNum': revocation_max,
                        'tag': rev_def_tag
                    }
                }
            )
            rev_def_id = r.json()['revocation_registry_definition_state']['revocation_registry_definition_id']
        except:
            pass
        
        r = requests.post(
            f'{self.endpoint}/anoncreds/revocation-list',
            # headers=self.headers,
            json={
                'options': options,
                'rev_reg_def_id': rev_def_id
            }
        )
        print(r.text)
        print(schema_id)
        print(cred_def_id)
        print(rev_def_id)
        await AskarStorage().update(
            'demo', 'default', {
                'schema_id': schema_id,
                'schema_url': id_to_url(schema_id),
                'cred_def_id': cred_def_id,
                'cred_def_url': id_to_url(cred_def_id),
                'rev_def_id': rev_def_id,
                'rev_def_url': id_to_url(rev_def_id)
            }
        )
        
    def bind_key(self, verification_method, public_key_multibase):
        r = requests.put(
            f'{self.endpoint}/wallet/keys',
            json={
                'kid': verification_method,
                'multikey': public_key_multibase
            }
        )
        
    
    def offer_credential(self, alias, cred_def_id, attributes):
        cred_offer = self.create_cred_offer(cred_def_id, attributes)
        invitation = self.create_oob_inv(
            alias=alias, 
            cred_ex_id=cred_offer['cred_ex_id'], 
            handshake=True
        )
        return cred_offer['cred_ex_id'], invitation
    
    def create_cred_offer(self, cred_def_id, attributes):
        endpoint = f'{self.endpoint}/issue-credential-2.0/create'
        cred_offer = {
            'auto_remove': False,
            'credential_preview': {
                "@type": "issue-credential/2.0/credential-preview",
                "attributes": [
                    {
                        "name": attribute,
                        "value": attributes[attribute]
                    } for attribute in attributes
                ]
            },
            'filter': {
                'anoncreds': {
                    'cred_def_id': cred_def_id,
                }
            }
        }
        r = requests.post(
            endpoint,
            # headers=self.headers,
            json=cred_offer
        )
        print(r.text)
        try:
            return r.json()
        except:
            raise AgentControllerError('No exchange')
    
    def request_presentation(self, name, cred_def_id, attributes):
        pres_req = self.create_pres_req(name, cred_def_id, attributes)
        invitation = self.create_oob_inv(
            pres_ex_id=pres_req['pres_ex_id'], 
            handshake=False
        )
        return pres_req['pres_ex_id'], invitation
        
    def create_pres_req(self, name, cred_def_id, attributes):
        endpoint = f'{self.endpoint}/present-proof-2.0/create-request'
        pres_req = {
            'auto_remove': False,
            'auto_verify': True,
            'presentation_request': {
                'anoncreds': {
                    'name': name,
                    'version': '1.0',
                    'nonce': str(randint(1, 99999999)),
                    'requested_attributes': {
                        'requestedAttributes': {
                            'names': attributes,
                            'restrictions':[
                                {
                                    'cred_def_id': cred_def_id
                                }
                            ]
                        }
                    },
                    'requested_predicates': {}
                }
            }
        }
        r = requests.post(
            endpoint,
            # headers=self.headers,
            json=pres_req
        )
        try:
            return r.json()
        except:
            raise AgentControllerError('No exchange')
    
    def create_oob_inv(self, alias=None, cred_ex_id=None, pres_ex_id=None, handshake=False):
        endpoint = f'{self.endpoint}/out-of-band/create-invitation?auto_accept=true'
        invitation = {
            "my_label": self.label,
            "attachments": [],
            "handshake_protocols": [],
        }
        if pres_ex_id:
            invitation['attachments'].append({
                "id":   pres_ex_id,
                "type": "present-proof"
            })
        if cred_ex_id:
            invitation['attachments'].append({
                "id":   cred_ex_id,
                "type": "credential-offer"
            })
        if handshake:
            invitation['alias'] = alias
            invitation['handshake_protocols'].append(
                "https://didcomm.org/didexchange/1.0"
            )
        r = requests.post(
            endpoint,
            # headers=self.headers,
            json=invitation
        )
        try:
            return r.json()['invitation']
        except:
            raise AgentControllerError('No invitation')
        
    def verify_presentation(self, pres_ex_id):
        endpoint = f'{self.endpoint}/present-proof-2.0/records/{pres_ex_id}'
        r = requests.get(
            endpoint,
            # headers=self.headers
        )
        try:
            return r.json()
        except:
            raise AgentControllerError('No exchange')

    
    def create_oob_connection(self, client_id):
        endpoint = f'{self.endpoint}/out-of-band/create-invitation?auto_accept=true'
        invitation = {
            "alias": client_id,
            "my_label": client_id,
            "handshake_protocols": ["https://didcomm.org/didexchange/1.0"],
        }
        r = requests.post(
            endpoint,
            json=invitation
        )
        try:
            return r.json()
        except:
            raise AgentControllerError('No invitation')
    
    def get_connection_id(self, client_id):
        endpoint = f'{self.endpoint}/connections?alias={client_id}'
        r = requests.get(
            endpoint
        )
        try:
            return r.json()['results'][0]
        except:
            raise AgentControllerError('No connection')
    
    def send_offer(self, connection_id, cred_def_id, attributes):
        endpoint = f'{self.endpoint}/issue-credential-2.0/send'
        cred_offer = {
            'auto_remove': False,
            'connection_id': connection_id,
            'credential_preview': {
                "@type": "issue-credential/2.0/credential-preview",
                "attributes": [
                    {
                        "name": attribute,
                        "value": attributes[attribute]
                    } for attribute in attributes
                ]
            },
            'filter': {
                'anoncreds': {
                    'cred_def_id': cred_def_id,
                }
            }
        }
        r = requests.post(
            endpoint,
            json=cred_offer
        )
        print(r.text)
    
    def send_request(self, connection_id, name, cred_def_id, attributes):
        endpoint = f'{self.endpoint}/present-proof-2.0/send-request'
        pres_req = {
            'auto_remove': False,
            'auto_verify': True,
            'connection_id': connection_id,
            'presentation_request': {
                'anoncreds': {
                    'name': name,
                    'version': '1.0',
                    'nonce': str(randint(1, 99999999)),
                    'requested_attributes': {
                        'requestedAttributes': {
                            'names': attributes,
                            'restrictions':[
                                {
                                    'cred_def_id': cred_def_id
                                }
                            ]
                        }
                    },
                    'requested_predicates': {}
                }
            }
        }
        r = requests.post(
            endpoint,
            json=pres_req
        )
        print(r.text)