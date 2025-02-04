

def id_to_url(resource_id):
    domain = resource_id.split(':')[3]
    namespace = resource_id.split(':')[4]
    identifier = resource_id.split(':')[5]
    return f'https://{domain}/{namespace}/{identifier}'