import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    birthDate = models.DateField(blank=True)
    memberDate = models.DateField(blank=True)
    renewalDate = models.DateField(blank=True)
    expireDate = models.DateField(blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='user_profiles/', blank=True)
    # active = models.BooleanField(default=False)

    def __str__(self):
        return f'User: {self.username} [ID: {self.id}]'
