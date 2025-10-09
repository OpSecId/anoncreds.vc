import hashlib
import requests
import urllib.parse
from config import Config


def query_from_issuer_id(issuer_id):
    domain = issuer_id.split(":")[3]
    scid = issuer_id.split(":")[2]
    return f"https://{domain}/explorer/dids?scid={scid}"


def query_from_resource_id(resource_id):
    domain = resource_id.split(":")[3]
    digest = resource_id.split("/")[-1].split(".")[0]
    return f"https://{domain}/explorer/resources?resource_id={digest}"


def hash(value):
    return hashlib.md5(value.lower().encode("utf-8")).hexdigest()


def demo_id(demo):
    return hashlib.sha1((demo.get("name") + demo.get("version")).encode()).hexdigest()


def id_to_resolver_link(resource_id):
    return f"{Config.ENDPOINT}/resource?id={url_encode(resource_id)}"


def id_to_url(resource_id):
    domain = resource_id.split(":")[3]
    namespace = resource_id.split(":")[4]
    identifier = resource_id.split(":")[5]
    return f"https://{domain}/{namespace}/{identifier}"


def fetch_resource(resource_id):
    r = requests.get(id_to_url(url_decode(resource_id)))
    return r.json()


def url_encode(value):
    return urllib.parse.quote(value, safe="")


def url_decode(value):
    return urllib.parse.unquote(value)
