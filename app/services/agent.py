import os
import uuid
import requests
from app.services import AskarStorage
from config import Config


class AgentController:
    def __init__(self):
        self.label = "Demo Issuer"
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
        # await self.setup_anoncreds()
        
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
        print('Setting up AnonCreds')
        options = {
            'verificationMethod': f'{self.did_webvh}#key-01',
            'serviceEndpoint': f'{self.webvh_server}/resources'
        }
        issuer_id = self.did_webvh
        schema_name = 'ExampleCredential'
        schema_version = '1.0'
        schema_attributes = ['name', 'description']
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
        # print(r.text)
        print(schema_id)
        print(cred_def_id)
        print(rev_def_id)
        
    def bind_key(self, verification_method, public_key_multibase):
        r = requests.put(
            f'{self.endpoint}/wallet/keys',
            json={
                'kid': verification_method,
                'multikey': public_key_multibase
            }
        )
        
    def create_invitation(self, alias):
        payload = {
            "alias": alias,
            "handshake_protocols": [
                "https://didcomm.org/didexchange/1.0"
            ],
            "my_label": self.label
        }
        r = requests.post(
            f'{self.endpoint}/out-of-band/create-invitation',
            headers=self.headers,
            json=payload
        )
        return r.json()
