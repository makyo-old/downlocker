from django.db import models
from downlocker.usermgmt.models import Client

class Resource(models.Model):
    client = models.ForeignKey(Client)
    resource_file = models.FileField(upload_to = file_path)
    mime_type = models.CharField(max_length = 50)
    file_digest = models.CharField(max_length = 40)
    watermark_text = models.CharField(max_length = 140, blank = True)
    watermark_visible = models.BooleanField(default = False)
    watermark_stego = models.BooleanField(default = False)
    watermark_invisible = models.BooleanField(default = False)
    require_nonce = models.BooleanField(default = False)
    dnp = models.BooleanField(default = False)
    client_resource_url = models.CharField(max_length = 2083)
    ctime = models.DateTimeField(auto_now_add = True)
    mtime = models.DateTimeField(auto_now = True)

    def file_path(instance, filename):
        return "%s/%s" % (instance.vendor, filename)

class AccessNonce(models.Model):
    download = models.ForeignKey('Resource')
    number = models.CharField(max_length = 40)
    times_viewed = models.IntegerField(default = 0)
    times_allowed = models.IntegerField(default = 1)
