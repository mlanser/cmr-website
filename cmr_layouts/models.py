import uuid

from django.db import models

from roadnames.models import RoadName

# from members.models import Member


SCALES = [
    ('Z', 'Z Scale'),
    ('N', 'N Scale'),
    ('HO', 'HO Scale'),
    ('S', 'S Scale'),
    ('O', 'O Scale'),
    ('G', 'G Scale'),
    ('Other', 'Other Scale'),
]

STATUS = [
    ('Operational', 'Operational'),
    ('Under Repair', 'Under Repair'),
    ('In Storage', 'In Storage'),
    ('Retired', 'Retired'),
]


class Locomotive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modelName = models.CharField(max_length=100)
    roadName = models.ForeignKey(RoadName, on_delete=models.SET_NULL, blank=True, null=True)
    roadNumber = models.CharField(max_length=12, blank=True)
    # member = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True)
    dccID = models.IntegerField(blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    scale = models.CharField(max_length=5, choices=SCALES, default='HO')
    image = models.ImageField(upload_to='roster/', blank=True)
    status = models.CharField(max_length=16, choices=STATUS, default='Operational')
    description = models.TextField(blank=True)

    def __str__(self):
        return (
            f'CMR Locomotive: {self.roadName} {self.modelName} #{self.roadNumber} [ID: {self.id}]'
        )


class RollingStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modelName = models.CharField(max_length=100)
    roadName = models.ForeignKey(RoadName, on_delete=models.SET_NULL, blank=True, null=True)
    roadNumber = models.CharField(max_length=12, blank=True)
    # member = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    scale = models.CharField(max_length=5, choices=SCALES, default='HO')
    image = models.ImageField(upload_to='roster/', blank=True)
    status = models.CharField(max_length=16, choices=STATUS, default='Operational')
    description = models.TextField(blank=True)

    def __str__(self):
        return f'CMR Rolling Stock: {self.roadName} {self.modelName} #{self.roadNumber} [ID: {self.id}]'


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    shortName = models.CharField(max_length=12, blank=True)
    scale = models.CharField(max_length=5, choices=SCALES, default='HO')
    description = models.TextField(blank=True)

    def __str__(self):
        return f'CMR Location: {self.name} [ID: {self.id}]'


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    shortName = models.CharField(max_length=12, blank=True)
    industry = models.CharField(max_length=64, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    scale = models.CharField(max_length=5, choices=SCALES, default='HO')
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='customer_logos/', blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'CMR Customer: {self.name} [ID: {self.id}]'
