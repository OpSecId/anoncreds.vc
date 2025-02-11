import hashlib

def hash(value):
    return hashlib.md5(value.lower().encode('utf-8')).hexdigest()

def demo_id(demo):
    return hashlib.sha1((demo.get('name')+demo.get('version')).encode()).hexdigest()

def id_to_url(resource_id):
    domain = resource_id.split(':')[3]
    namespace = resource_id.split(':')[4]
    identifier = resource_id.split(':')[5]
    return f'https://{domain}/{namespace}/{identifier}'