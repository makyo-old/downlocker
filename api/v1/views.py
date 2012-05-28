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
        """
        Returns information about a given nonce without incrementing usage

        Does not require auth
        """
        try:
            n = Nonce.objects.get(number__exact = nonce)
        except Nonce.DoesNotExist:
            response = HttpResponse("<response><error>Nonce does not exist</error></response>", mimetype = "application/xml")
            response.status_code = 404
            return response
            
        t = Template("""
        <response>
          <nonce>
            <id>{{ id }}</id>
            <client>
              <id>{{ client_id }}</id>
              <client_token>{{ client_token }}</client_token>
            </client>
            <number>{{ number }}</number>
            <times_allowed>{{ times_allowed }}</times_allowed>
            <times_viewed>{{ times_viewed }}</times_viewed>
            <active>{{ active }}</active>
          </nonce>
        </response>
                """)
        c = Context({
            id: n.id,
            client_id: n.client.id,
            client_token: n.client_token,
            number: n.number,
            times_allowed: n.times_allowed,
            times_viewed: n.times_viewed,
            active: n.active
            })
        return HttpResponse(t.render(c), mimetype = 'application/xml')
    def post():
        pass
    def put():
        from time import time

        # parse request.body xml: <request><client_token>asdf...</client_token></request>, possibly with times_allowed and active as well
        
        try:
            client = Client.objects.get(token__exact = client_token)
        except Client.DoesNotExist:
            response = HttpResponse("<response><error>Client does not exist</error></response>", mimetype = "application/xml")
            response.status_code = 404
            return response
        sha = hashlib.sha1()
        sha.update("%f:%s" % (time(), client_token))
        nonce = Nonce(client = client, number = sha.hexdigest())
        nonce.save()
        t = Template("<response><nonce>{{ nonce }}</nonce></response>")
        c = Context({'nonce': nonce.number})
        return HttpResponse(t.render(c), mimetype = 'application/xml')
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
        try:
            client = Client.objects.get(token__exact = client_token)
        except Client.DoesNotExist:
            response = HttpResponse("<response><error>Client does not exist</error></response>", mimetype = "application/xml")
            response.status_code = 404
            return response
        try:
            r = Resource.objects.get(client__exact = client, remote_resource_id__exact = remote_resource_id)
        except Resource.DoesNotExist:
            response = HttpResponse("<response><error>Resource does not exist</error></response>", mimetype = "application/xml")
            response.status_code = 404
            return response
        if r.public or _check_auth(request.GET.get('nonce', None), request.GET.get('auth_token', None)):
            response = HttpResponse(mimetype = r.mime_type)
            response['X-Sendfile'] = smart_str("filename") # TODO
            response['Content-length'] = r.resource_file.length # TODO
            return response
        else:
            response = HttpResponse("<response><error>Resource is not public and authorization failed</error></response>", mimetype = "application/xml")
            response.status_code = 403
            return response
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

def metadata_dispatcher(request, client_token, remote_resource_id):
    # PUT - unused
    # POST - modifies a resource's metadata
    # GET - returns a resource's metadata
    # DELETE - unused
    # HEAD - checks to see if a resource exists

    def get():
        pass
    def post():
        pass
    def put():
        response = HttpResponse("<response><error>Request method not supported</error></response>", mimetype = "application/xml")
        response.status_code = 405
        response['Allow'] = "GET,POST,HEAD"
        return response
    def delete():
        response = HttpResponse("<response><error>Request method not supported</error></response>", mimetype = "application/xml")
        response.status_code = 405
        response['Allow'] = "GET,POST,HEAD"
        return response
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
        response = HttpResponse("<response><error>Request method not supported</error></response>", mimetype = "application/xml")
        response.status_code = 405
        response['Allow'] = "GET,POST,HEAD"
        return response
    def delete():
        response = HttpResponse("<response><error>Request method not supported</error></response>", mimetype = "application/xml")
        response.status_code = 405
        response['Allow'] = "GET,POST,HEAD"
        return response
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
