from django.db import models

class Download(models.Model):
    vendor = models.ForeignKey('Vendor')
    download_file = models.FileField(upload_to = file_path)
    mime_type = models.CharField(max_length = 50)
    file_digest = models.CharField(max_length = 40)
    watermark_text = models.CharField(max_length = 140, blank = True)
    watermark_visible = models.BooleanField(default = False)
    watermark_stego = models.BooleanField(default = False)
    watermark_invisible = models.BooleanField(default = False)
    require_nonce = models.BooleanField(default = False)

    def file_path(instance, filename):
        return "%s/%s" % (instance.vendor, filename)

class Nonce(models.Model):
    download = models.ForeignKey('Download')
    number = models.IntegerField()
    times_viewed = models.IntegerField(default = 0)
    times_allowed = models.IntegerField(default = 1)

class Vendor(models.Model):
    #oauth ish
