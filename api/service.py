from downlocker.resources.models import Nonce
from django.http import HttpResponse

def check_auth(auth_tag):
    nonce = _get_text(auth_tag.getElementsByTagName('nonce')[0].childNodes)
    auth_token = _get_text(auth_tag.getElementsByTagName('auth_token')[0].childNodes)
    n = Nonce.objects.get(number__exact = nonce)
    c = n.client
    sha = hashlib.sha1()
    sha.update('%s:%s:%s' % (c.token, c.secret, nonce))
    return (auth_token == sha.hexdigest())

def get_text(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def auth_fail(resource, method):
    response = HttpResponse("<response><error>Resource [%s] accessed with method [%s] requires authentication</error></response>" % (resource, method), mimetype = "application/xml")
    response.status_code = 403
    return response

def not_found(resource):
    response = HttpResponse("<response><error>Resource [%s] does not exist</error></response>" % resource, mimetype = "application/xml")
    response.status_code = 404
    return response

