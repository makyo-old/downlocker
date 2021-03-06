import hashlib
from django.http import HttpResponse
from django.template import Template, Context
from downlocker.resources.models import *
from downlocker.usermgmt.models import *
from downlocker.api.service import *

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
            return not_found('nonce')
            
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
        """
        Increments nonce usage without requesting a resource

        Requires auth
        """
        from xml.dom.minidom import parseString

        # parse request.body xml: <request><auth><nonce>...</nonce><auth_token>...</auth_token></auth></request>
        body = parseString(request.body)
        auth = body.getElementsByTagName('auth')[0]
        if check_auth(auth):
            try:
                n = Nonce.objects.get(number__exact = nonce)
            except Nonce.DoesNotExist:
                return not_found('nonce')
            if n.times_viewed < n.times_allowed:
                n.times_viewed += 1
                if n.times_viewed == n.times_allowed:
                    n.active = False
                n.save()
            return HttpResponse("<response><success>true</success></response>", mimetype = "application/xml")
        else:
            return auth_fail('nonce', 'POST')
    def put():
        """
        Creates a nonce and returns it

        Does not require auth
        """
        from time import time
        from xml.dom.minidom import parseString

        # parse request.body xml: <request><client_token>...</client_token></request>
        body = parseString(request.body)
        client_token = get_text(body.getElementsByTagName('client_token')[0].childNodes)
        
        try:
            client = Client.objects.get(token__exact = client_token)
        except Client.DoesNotExist:
            return not_found('client')
        client.max_nonce += 1
        sha = hashlib.sha1()
        sha.update("%f:%s:%d" % (time(), client_token, client.max_nonce))
        nonce = Nonce(client = client, number = sha.hexdigest())
        nonce.save()
        client.save()
        t = Template("<response><nonce>{{ nonce }}</nonce></response>")
        c = Context({'nonce': nonce.number})
        return HttpResponse(t.render(c), mimetype = 'application/xml')
    def delete():
        """
        Expires a nonce

        Requires auth
        """
        from xml.dom.minidom import parseString

        # parse request.body xml: <request><auth><nonce>...</nonce><auth_token>...</auth_token></auth></request>
        body = parseString(request.body)
        auth = body.getElementsByTagName('auth')[0]
        if check_auth(auth):
            try:
                n = Nonce.objects.get(number__exact = nonce)
            except Nonce.DoesNotExist:
                return not_found('nonce')
            n.active = False
            n.save()
        else:
            return auth_fail('nonce', 'DELETE')
    def head():
        """
        Checks to see if a nonce exists and is usable

        Does not require auth
        """
        try:
            n = Nonce.objects.get(number__exact = nonce)
        except Nonce.DoesNotExist:
            return not_found('nonce')
        if n.active == True:
            return HttpResponse("<response><success>true</success></response>", mimetype = "application/xml")
        else:
            response = HttpResponse("<response><error>Nonce found, but is no longer active</error></response", mimetype = "application/xml")
            response.status_code = 410
            return response

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
        """
        Returns a resource

        Does not require auth
        """
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
        # TODO just redirect to file
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
