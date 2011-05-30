from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length = 40, unique = True)
    secret = models.CharField(max_length = 40)

class Nonce(models.Model):
    client = models.ForeignKey('Client')
    number = models.CharField(max_length = 40)
