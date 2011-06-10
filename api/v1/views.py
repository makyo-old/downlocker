import hashlib
from django.http import HttpResponse
from django.template import Template, Context
from downlocker.download.models import *
from downlocker.usermgmt.models import *

def request_nonce(request, client_token):
    from time import time
    
    try:
        client = Client.objects.get(token__exact = client_token)
    except Client.DoesNotExist:
        response = HttpResponse("<response><error>Client does not exist</error></response>", mimetype = "application/xml")
        response.status_code = 404
        return response
    sha = hashlib.sha1()
    sha.update("%f:%s" * (time(), client_token))
    nonce = Nonce(client = client, number = sha.hexdigest())
    nonce.save()
    t = Template("<response><nonce>{{ nonce }}</nonce></response>")
    c = Context({'nonce': nonce.number})
    return HttpResponse(t.render(c), mimetype = 'application/xml')

def request_resource_url(request, nonce, auth_token):
    n = Nonce.objects.get(number__exact = nonce)
    if (!_check_auth(n, auth_token)):
        response = HttpResponse("<response><error>Permission denied: authentication token mismatch</error></response>", mimetype="application/xml")
        response.status_code = 403
        return response
    resource_file = request.REQUEST.get('resourceFile', None)
    if resource_file is None:
        response = HttpResponse("<response><error>Missing parameter: resourceFile</error></response>", mimetype="application/xml")
        response.status_code = 500
        return response
    resource = Resource.objects.get(original_filename__exact = resource_file, client__id__exact = n.client.id)

def read_resource(request, nonce, auth_token):
    pass

def create_resource(request, nonce, auth_token):
    pass

def update_resource(request, nonce, auth_token):
    pass

def delete_resource(request, nonce, auth_token):
    pass

def mirror_resource(request, nonce, auth_token):
    pass

def resource_exists(request):
    pass

def _check_auth(nonce, auth_token):
    c = nonce.client
    sha = hashlib.sha1()
    sha.update('%s:%s:%s' % (c.token, c.secret, nonce.number))
    return (auth_token == sha.hexdigest())
