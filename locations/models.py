from datetime import datetime

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from base.blocks import BaseStreamBlock
from locations.choices import DAY_CHOICES


class OperatingHours(models.Model):
    """
    Standard Django model to manage operating hours for a given Location
    """

    day_of_week = models.CharField(
        max_length=3, 
        choices=DAY_CHOICES, 
        default="MON"
    )
    time_open = models.TimeField(blank=True, null=True)
    time_close = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(
        "is closed?", 
        blank=True, 
        help_text="Check if location is closed on this day"
    )
    holiday_text = models.CharField(
        max_length=255, 
        blank=True, 
    )

    panels = [
        FieldPanel("day_of_week"),
        FieldPanel("time_open"),
        FieldPanel("time_close"),
        FieldPanel("closed"),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        open_time = self.opening_time.strftime("%H:%M") if self.time_open else "--"
        close_time = self.closing_time.strftime("%H:%M") if self.time_close else "--"

        return f"{self.day}: {open_time} - {close_time} {settings.TIME_ZONE}"


class LocationOperatingHours(Orderable, OperatingHours):
    """
    A model creating a relationship between the OperatingHours and Location
    Note that unlike BlogPersonRelationship we don't include a ForeignKey to
    OperatingHours as we don't need that relationship (e.g. any Location open
    a certain day of the week). The ParentalKey is the minimum required to
    relate the two objects to one another. We use the ParentalKey's related_
    name to access it from the LocationPage admin
    """

    location = ParentalKey(
        "LocationPage", 
        related_name="hours_of_operation", 
        on_delete=models.CASCADE
    )


class LocationsIndexPage(Page):
    """
    A Page model that creates an index page (a listview)
    """

    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    # Only LocationPage objects can be added underneath this index page
    subpage_types = ["LocationPage"]

    # Allows children of this indexpage to be accessible via the indexpage
    # object on templates. We use this on the homepage to show featured
    # sections of the site and their child pages
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child
    # items, that are live, by the title alphabetical order.
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(LocationsIndexPage, self).get_context(request)
        context["locations"] = (
            LocationPage.objects.descendant_of(self).live().order_by("title")
        )
        return context

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image"),
    ]


class LocationPage(Page):
    """
    Detail for a specific bakery location.
    """

    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(
        BaseStreamBlock(), 
        verbose_name="Page body", 
        blank=True, 
        use_json_field=True
    )
    address = models.TextField()
    lat_long = models.CharField(
        max_length=36,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[
            RegexValidator(
                regex=r"^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$",
                message="Lat Long must be a comma-separated numeric lat and long",
                code="invalid_lat_long",
            ),
        ],
    )

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField("address"),
        index.SearchField("body"),
    ]

    # Fields to show to the editor in the admin view
    content_panels = [
        FieldPanel("title"),
        FieldPanel("introduction"),
        FieldPanel("image"),
        FieldPanel("body"),
        FieldPanel("address"),
        FieldPanel("lat_long"),
        InlinePanel("hours_of_operation", heading="Hours of Operation", label="Slot"),
    ]

    def __str__(self):
        return self.title

    @property
    def operating_hours(self):
        return self.hours_of_operation.all()

    # Determines if the location is currently open. It is timezone naive
    def is_open(self):
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a").upper()
        try:
            self.operating_hours.get(
                day_of_week=current_day,
                time_open__lte=current_time,
                time_close_time__gte=current_time,
            )
            return True
        except LocationOperatingHours.DoesNotExist:
            return False

    # Makes additional context available to the template so that we can access
    # the latitude, longitude and map API key to render the map
    def get_context(self, request):
        context = super(LocationPage, self).get_context(request)
        context["lat"] = self.lat_long.split(",")[0]
        context["long"] = self.lat_long.split(",")[1]
        context["google_map_api_key"] = settings.GOOGLE_MAP_API_KEY
        return context

    # Can only be placed under a LocationsIndexPage object
    parent_page_types = ["LocationsIndexPage"]
