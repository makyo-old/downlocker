from django.conf.urls.defaults import *

urlpatterns = patterns('downlocker.api.v1.views',
    (r'^resource((?P<client_token>.+)$', 'client_collection_dispatcher'),
    (r'^resource/(?P<client_token>.+)/(?P<remote_resource_id>.+)$', 'resource_dispatcher'),
    (r'^metadata/(?P<client_token>.+)/(?P<remote_resource_id>.+)$', 'metadata_dispatcher'),
    (r'^nonce/(?P<nonce>.*)', 'nonce_dispatcher'),
    #(r'^requestNonce/(?P<client_token>.+)/$', 'request_nonce'),
    #(r'^requestResourceURL/(?P<nonce>.+)/(?P<auth_token>.+)/$', 'request_resource_url'),
    #(r'^readResource/(?P<nonce>.+)/(?P<auth_token>.+)/$', 'read_resource'),
    #(r'^createResource/(?P<nonce>.+)/(?P<auth_token>.+)/$', 'create_resource'),
    #(r'^updateResource/(?P<nonce>.+)/(?P<auth_token>.+)/$', 'update_resource'),
    #(r'^deleteResource/(?P<nonce>.+)/(?P<auth_token>.+)/$', 'delete_resource'),
    #(r'^mirrorResource/(?P<nonce>.+)/(?P<auth_token>.+)/$', 'mirror_resource'),
    #(r'^resourceExists/$', 'resource_exists'),
)
