import hashlib
from django.http import HttpResponse
from django.template import Template, Context
from downlocker.download.models import *
from downlocker.usermgmt.models import *

def nonce_dispatcher(request, nonce):
    # PUT - creates a nonce and returns it
    # POST - increments nonce usage without requesting a resource
    # GET - returns information about the noce without incrementing usage
    # DELETE - expires a nonce
    # HEAD - checks to see if a nonce exists and is usable

    def get():
        pass
    def post():
        pass
    def put():
        pass
    def delete():
        pass
    def head():
        pass

    dispatch_map = {
            'GET': get,
            'POST': post,
            'PUT': put,
            'DELETE': delete,
            'HEAD': head
            }

    return dispatch_map[request.method]()


def resource_dispatcher(request, client_token, remote_resource_id):
    # PUT - creates/replaces a resource
    # POST - modifies a resource or its metadata
    # GET - returns a resource
    # DELETE - removes a resource
    # HEAD - checks to see if a resource exists

    def get():
        pass
    def post():
        pass
    def put():
        pass
    def delete():
        pass
    def head():
        pass

    dispatch_map = {
            'GET': get,
            'POST': post,
            'PUT': put,
            'DELETE': delete,
            'HEAD': head
            }

    return dispatch_map[request.method]()

def client_collection_dispatcher(request, client_token):
    # PUT - unused
    # POST - creates a resource in the collection
    # GET - lists the resources in the collection
    # DELETE - unused
    # HEAD - checks to see if the collection exists

    def get():
        pass
    def post():
        pass
    def put():
        pass
    def delete():
        pass
    def head():
        pass

    dispatch_map = {
            'GET': get,
            'POST': post,
            'PUT': put,
            'DELETE': delete,
            'HEAD': head
            }

    return dispatch_map[request.method]()

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
    resource_id = request.REQUEST.get('resourceId', None)
    if resource_id is None:
        response = HttpResponse("<response><error>Missing parameter: resourceId</error></response>", mimetype="application/xml")
        response.status_code = 500
        return response
    try:
        resource = Resource.objects.get(id__exact = resource_id)
    except Resource.DoesNotExist:
        response = HttpResponse("<response><error>Resource not found: resource id %s not found</error></response>" % resource_id, mimetype="application/xml")
        response.status_code = 404
        return response
    

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
