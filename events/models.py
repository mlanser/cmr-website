import uuid

from django.db import models


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    location = models.CharField(
        max_length=100
    )  # TODO: This should be a ForeignKey to a Location model
    image = models.ImageField(upload_to='events/images/')

    def __str__(self):
        return f'Location: {self.title} [ID: {self.id}]'
