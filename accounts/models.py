import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False) 
    is_active = models.BooleanField(default=False)  
    activation_token = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return self.username
