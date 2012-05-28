from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length = 40, unique = True)
    secret = models.CharField(max_length = 40)
    name = models.CharField(max_length = 200)
    description = models.TextField(blank = True)
    max_nonce = models.IntegerField(default = 0)
