import os
import requests
from app.services import AskarStorage
from config import Config


class AgentController:
    def __init__(self):
        self.label = "Demo Issuer"
        self.namespace = "demo"
        self.identifier = "issuer"
        self.issuer = None
        self.webvh_server = os.getenv('DIDWEBVH_SERVER')
        self.witness_key = os.getenv('DIDWEBVH_WITNESS_KEY')
        self.endpoint = os.getenv('AGENT_ADMIN_ENDPOINT')
        self.headers = {
            'X-API-KEY': os.getenv('AGENT_ADMIN_API_KEY')
        }
        
    async def provision(self):
        await AskarStorage().update('demo', 'default', {})
        # webvh_domain = self.webvh_server.split('://')[-1]
        # print('Updating witness key')
        # r = requests.put(
        #     f'{self.endpoint}/wallet/keys',
        #     headers=self.headers,
        #     json={
        #         'kid': f'webvh:{webvh_domain}@witnessKey',
        #         'multikey': self.witness_key
        #     }
        # )
        # print(r.text)
        # print('Configuring webvh')
        # r = requests.post(
        #     f'{self.endpoint}/did/webvh/configuration',
        #     headers=self.headers,
        #     json={
        #         'server_url': self.webvh_server,
        #         'witness_key': self.witness_key,
        #         'witness': True
        #     }
        # )
        # print(r.text)
        # print('Creating DID')
        # try:
        #     r = requests.post(
        #         f'{self.endpoint}/did/webvh/create',
        #         headers=self.headers,
        #         json={
        #             'options': {
        #                 'identifier': self.identifier,
        #                 'namespace': self.namespace,
        #                 'parameters': {
        #                     'portable': False,
        #                     'prerotation': False
        #                 }
        #             }
        #         }
        #     )
        #     print(r.text)
        #     pass
        # except:
        #     pass
        # did_web = f'did:web:{domain}:{self.namespace}:{self.identifier}'
        # try:
        #     print('Resolving webvh')
        #     r = requests.get(
        #         f'{self.endpoint}/resolver/resolve/{did_web}',
        #         headers=self.headers
        #     )
        #     print(r.text)
        #     did_document = r.json()['did_document']
        #     did_webvh = did_document.get('alsoKnownAs')[0]
        #     did_webvh_kid = did_document.get('verificationMethod')[0].get('id')
        #     issuer_info = {
        #         'id': did_webvh,
        #         'verificationMethod': did_webvh_kid
        #     }
        #     print(issuer_info)
        #     self.issuer = issuer_info
        # except:
        #     pass
        # await self.setup_anoncreds()
        
    def create_did_webvh(self):
        pass
        
    async def setup_anoncreds(self):
        print('Setting up anoncreds')
        issuer_id = self.issuer['id']
        schema_name = 'ExampleCredential'
        schema_version = '1.0'
        schema_attributes = ['name', 'description']
        # cred_def_tag = f'{schema_name}-def'
        # rev_def_tag = f'{schema_name}-rev'
        # revocation=True
        # revocation_max=8
        try:
            print('Creating schema')
            r = requests.post(
                f'{self.endpoint}/anoncreds/schema',
                headers=self.headers,
                json={
                    'options': {
                        'verificationMethod': self.issuer['verificationMethod'],
                        'serviceEndpoint': self.server
                    },
                    'schema': {
                        'attrNames': schema_attributes,
                        'issuerId': issuer_id,
                        'name': schema_name,
                        'version': schema_version
                    }
                }
            )
            print(r.text)
            schema_id = r.json()['schema_state']['schema_id']
            print(schema_id)
        except:
            pass
        
        # r = requests.post(
        #     f'{self.endpoint}/anoncreds/credential-definition',
        #     headers=self.headers,
        #     json={
        #         'options': {
        #             'support_revocation': revocation
        #         },
        #         'credential_definition': {
        #             'issuerId': issuer_id,
        #             'schemaId': schema_id,
        #             'tag': cred_def_tag,
        #         }
        #     }
        # )
        # cred_def_id = r.json()['credential_definition_state']['credential_definition_id']
        
        # r = requests.post(
        #     f'{self.endpoint}/anoncreds/revocation-registry-definition',
        #     headers=self.headers,
        #     json={
        #         'options': {},
        #         'revocation_registry_definition': {
        #             'credDefId': cred_def_id,
        #             'issuerId': issuer_id,
        #             'maxCredNum': revocation_max,
        #             'tag': rev_def_tag
        #         }
        #     }
        # )
        # rev_def_id = r.json()['revocation_registry_definition_state']['revocation_registry_definition_id']
        
        # r = requests.post(
        #     f'{self.endpoint}/anoncreds/revocation-list',
        #     headers=self.headers,
        #     json={
        #         'options': {},
        #         'rev_reg_def_id': rev_def_id
        #     }
        # )
        
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
