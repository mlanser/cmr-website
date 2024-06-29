import uuid

from django.db import models


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    street = models.CharField(max_length=254, blank=True)
    street2 = models.CharField(max_length=254, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip = models.CharField(max_length=100, blank=True)
    virtual = models.BooleanField(default=False)
    url = models.URLField(blank=True)
    map = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='locations/', blank=True)

    def __str__(self):
        return f'Location: {self.name} [ID: {self.id}]'
