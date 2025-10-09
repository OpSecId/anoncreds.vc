import uuid
import requests
from app.utils import url_encode
from config import Config
from random import randint


class AgentControllerError(Exception):
    """Generic AgentControllerError Error."""


class AgentController:
    def __init__(self):
        self.endpoint = Config.AGENT_ADMIN_ENDPOINT
        if Config.AGENT_MODE == "single":
            self.headers = {"X-API-KEY": Config.AGENT_ADMIN_API_KEY}
        elif Config.AGENT_MODE == "multi":
            self.headers = {"Authorization": None}

    def set_token(self, token):
        self.headers["Authorization"] = f"Bearer {token}"

    def _try_return(self, response):
        try:
            return response.json()

        except Exception:
            print(f"Agent error {response.status_code} {response.text}")
            raise AgentControllerError(
                f"Agent error {response.status_code} {response.text}"
            )

    def configure_plugin(self):
        return self._try_return(
            requests.post(
                f"{self.endpoint}/did/webvh/configuration",
                headers=self.headers,
                json={
                    "server_url": Config.WEBVH_SERVER,
                    "witness": True,
                },
            )
        )

    def create_did(self):
        return self._try_return(
            requests.post(
                f"{self.endpoint}/did/webvh/create",
                headers=self.headers,
                json={
                    "options": {
                        "namespace": "demo",
                        "identifier": str(uuid.uuid4())[:6],
                    }
                },
            )
        )

    def create_schema(self, issuer_id):
        return self._try_return(
            response=requests.post(
                f"{self.endpoint}/anoncreds/schema",
                headers=self.headers,
                json={
                    "schema": {
                        "name": Config.DEMO["credential"]["name"],
                        "version": Config.DEMO["credential"]["version"],
                        "issuerId": issuer_id,
                        "attrNames": [
                            attribute
                            for attribute in Config.DEMO["credential"]["attributes"]
                        ],
                    }
                },
            )
        )

    def create_cred_def(self, schema_id):
        return self._try_return(
            response=requests.post(
                f"{self.endpoint}/anoncreds/credential-definition",
                headers=self.headers,
                json={
                    "options": {
                        "support_revocation": True,
                        "revocation_registry_size": Config.DEMO["registrySize"],
                    },
                    "credential_definition": {
                        "issuerId": schema_id.split("/")[0],
                        "schemaId": schema_id,
                        "tag": Config.DEMO["credential"]["name"],
                    },
                },
            )
        )

    def get_active_registry(self, cred_def_id):
        return self._try_return(
            requests.get(
                f"{self.endpoint}/anoncreds/revocation/active-registry/{url_encode(cred_def_id)}",
                headers=self.headers,
            )
        )

    def create_invitation(self):
        return self._try_return(
            requests.post(
                f"{self.endpoint}/out-of-band/create-invitation",
                headers=self.headers,
                json={
                    # "my_label": Config.DEMO['issuer']['name'],
                    "handshake_protocols": ["https://didcomm.org/didexchange/1.1"]
                },
            )
        )

    def find_connection(self, invitation_id):
        return self._try_return(
            requests.get(
                f"{self.endpoint}/connections",
                headers=self.headers,
                params={"invitation_msg_id": invitation_id},
            )
        )

    def get_connection(self, connection_id):
        return self._try_return(
            requests.get(
                f"{self.endpoint}/connections/{connection_id}", headers=self.headers
            )
        )

    def send_credential_offer(self, connection_id, cred_def_id):
        return self._try_return(
            requests.post(
                f"{self.endpoint}/issue-credential-2.0/send",
                headers=self.headers,
                json={
                    "auto_remove": False,
                    "connection_id": connection_id,
                    "credential_preview": {
                        "@type": "issue-credential/2.0/credential-preview",
                        "attributes": [
                            {
                                "name": attribute,
                                "value": Config.DEMO["credential"]["attributes"][
                                    attribute
                                ],
                            }
                            for attribute in Config.DEMO["credential"]["attributes"]
                        ],
                    },
                    "filter": {
                        "anoncreds": {
                            "cred_def_id": cred_def_id,
                        }
                    },
                },
            )
        )

    def get_credential_exchange(self, cred_ex_id):
        return self._try_return(
            requests.get(
                f"{self.endpoint}/issue-credential-2.0/records/{cred_ex_id}",
                headers=self.headers,
            )
        )

    def send_presentation_request(self, connection_id, cred_def_id, timestamp):
        return self._try_return(
            requests.post(
                f"{self.endpoint}/present-proof-2.0/send-request",
                headers=self.headers,
                json={
                    "auto_remove": False,
                    "auto_verify": True,
                    "connection_id": connection_id,
                    "presentation_request": {
                        "anoncreds": {
                            "name": Config.DEMO["presentation"]["name"],
                            "version": Config.DEMO["presentation"]["version"],
                            "nonce": str(randint(1, 99999999)),
                            "requested_attributes": {
                                "requestedAttributes": {
                                    "names": Config.DEMO["presentation"]["attributes"],
                                    "restrictions": [{"cred_def_id": cred_def_id}],
                                }
                            }
                            if Config.DEMO["presentation"]["attributes"]
                            else {},
                            "requested_predicates": {
                                "requestedPredicate": {
                                    "name": Config.DEMO["presentation"]["predicate"][0],
                                    "p_type": Config.DEMO["presentation"]["predicate"][
                                        1
                                    ],
                                    "p_value": Config.DEMO["presentation"]["predicate"][
                                        2
                                    ],
                                    "restrictions": [{"cred_def_id": cred_def_id}],
                                }
                            }
                            if Config.DEMO["presentation"]["predicate"]
                            else {},
                            "non_revoked": {"from": timestamp, "to": timestamp}
                            if timestamp
                            else {},
                        }
                    },
                },
            )
        )

    def get_presentation_exchange(self, pres_ex_id):
        return self._try_return(
            requests.get(
                f"{self.endpoint}/present-proof-2.0/records/{pres_ex_id}",
                headers=self.headers,
            )
        )

    def revoke_credential(self, cred_ex_id):
        return self._try_return(
            requests.post(
                f"{self.endpoint}/anoncreds/revocation/revoke",
                headers=self.headers,
                json={"cred_ex_id": cred_ex_id, "publish": True},
            )
        )

    def get_did_webvh_configuration(self):
        return self._try_return(
            requests.get(
                f"{self.endpoint}/did/webvh/configuration",
                headers=self.tenant_headers,
            )
        )

    def offer_credential(self, alias, cred_def_id, attributes):
        cred_offer = self.create_cred_offer(cred_def_id, attributes)
        invitation = self.create_oob_inv(
            alias=alias, cred_ex_id=cred_offer["cred_ex_id"], handshake=True
        )
        return cred_offer["cred_ex_id"], invitation

    def create_cred_offer(self, cred_def_id, attributes):
        endpoint = f"{self.endpoint}/issue-credential-2.0/create"
        cred_offer = {
            "auto_remove": False,
            "credential_preview": {
                "@type": "issue-credential/2.0/credential-preview",
                "attributes": [
                    {"name": attribute, "value": attributes[attribute]}
                    for attribute in attributes
                ],
            },
            "filter": {
                "anoncreds": {
                    "cred_def_id": cred_def_id,
                }
            },
        }
        r = requests.post(endpoint, headers=self.headers, json=cred_offer)
        print(r.text)
        try:
            return r.json()
        except:
            raise AgentControllerError("No exchange")

    def request_presentation(self, name, cred_def_id, attributes):
        pres_req = self.create_pres_req(name, cred_def_id, attributes)
        invitation = self.create_oob_inv(
            pres_ex_id=pres_req["pres_ex_id"], handshake=False
        )
        return pres_req["pres_ex_id"], invitation

    def create_pres_req(self, name, cred_def_id, attributes):
        endpoint = f"{self.endpoint}/present-proof-2.0/create-request"
        pres_req = {
            "auto_remove": False,
            "auto_verify": True,
            "presentation_request": {
                "anoncreds": {
                    "name": name,
                    "version": self.demo.get("version"),
                    "nonce": str(randint(1, 99999999)),
                    "requested_attributes": {
                        "requestedAttributes": {
                            "names": attributes,
                            "restrictions": [{"cred_def_id": cred_def_id}],
                        }
                    },
                    "requested_predicates": {},
                }
            },
        }
        r = requests.post(endpoint, headers=self.headers, json=pres_req)
        try:
            return r.json()
        except:
            raise AgentControllerError("No exchange")

    def create_oob_inv(
        self, alias=None, cred_ex_id=None, pres_ex_id=None, handshake=False
    ):
        endpoint = f"{self.endpoint}/out-of-band/create-invitation?auto_accept=true"
        invitation = {
            "my_label": self.issuer_name,
            "attachments": [],
            "handshake_protocols": [],
        }
        if pres_ex_id:
            invitation["attachments"].append(
                {"id": pres_ex_id, "type": "present-proof"}
            )
        if cred_ex_id:
            invitation["attachments"].append(
                {"id": cred_ex_id, "type": "credential-offer"}
            )
        if handshake:
            invitation["alias"] = alias
            invitation["handshake_protocols"].append(
                "https://didcomm.org/didexchange/1.0"
            )
        r = requests.post(endpoint, headers=self.headers, json=invitation)
        try:
            return r.json()["invitation"]
        except:
            raise AgentControllerError("No invitation")

    def verify_presentation(self, pres_ex_id):
        endpoint = f"{self.endpoint}/present-proof-2.0/records/{pres_ex_id}"
        r = requests.get(endpoint, headers=self.headers)
        try:
            return r.json()
        except:
            raise AgentControllerError("No exchange")

    def verify_offer(self, cred_ex_id):
        endpoint = f"{self.endpoint}/issue-credential-2.0/records/{cred_ex_id}"
        r = requests.get(endpoint, headers=self.headers)
        try:
            return r.json().get("cred_ex_record")
        except:
            raise AgentControllerError("No exchange")

    def create_oob_connection(self, client_id):
        endpoint = f"{self.endpoint}/out-of-band/create-invitation"
        invitation = {
            "alias": client_id,
            "my_label": self.issuer_name,
            "handshake_protocols": ["https://didcomm.org/didexchange/1.1"],
        }
        r = requests.post(endpoint, headers=self.headers, json=invitation)
        try:
            return r.json()
        except:
            raise AgentControllerError("No invitation")

    def get_connection_from_alias(self, client_id):
        endpoint = f"{self.endpoint}/connections?alias={client_id}"
        r = requests.get(
            endpoint,
            headers=self.headers,
        )
        try:
            return r.json()["results"][0]
        except:
            raise AgentControllerError("No connection")

    def get_latest_sl(self, cred_def_id):
        rev_def_id = self.get_registry(cred_def_id)["result"]["revoc_reg_id"]
        status_list = self.get_status_list(rev_def_id)["content"]["revocationList"]
        return status_list

    def send_message(self, connection_id, message=None):
        requests.post(
            f"{self.endpoint}/connections/{connection_id}/send-message",
            headers=self.headers,
            json={"content": message or "Greetings"},
        )
