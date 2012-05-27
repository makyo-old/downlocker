from django.db import models
from downlocker.usermgmt.models import Client

class Resource(models.Model):
    client = models.ForeignKey(Client)
    resource_file = models.FileField(upload_to = file_path)
    remote_resource_id = models.CharField(max_length = 200)
    mime_type = models.CharField(max_length = 50)
    file_digest = models.CharField(max_length = 40)
    public = models.BooleanField(default = False)
    ctime = models.DateTimeField(auto_now_add = True)
    mtime = models.DateTimeField(auto_now = True)

    def file_path(instance, filename):
        return "%s/%s" % (instance.vendor, filename)

def ResourceAttribute(models.model):
    resource = models.ForeignKey('Resource')
    key = models.CharField(max_length = 50)
    value = models.CharField(max_length = 500)

class Nonce(models.Model):
    client = models.ForeignKey(Client)
    number = models.CharField(max_length = 40)
    times_viewed = models.IntegerField(default = 0)
    times_allowed = models.IntegerField(default = 1)
    active = models.BooleanField(default = True)
