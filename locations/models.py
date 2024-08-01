from datetime import datetime

from django.conf import settings
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from base.blocks import BaseStreamBlock
from locations.choices import DAY_CHOICES


class OperatingHours(models.Model):
    """
    Standard Django model to manage operating hours
    for a given `Location` object.
    """

    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, default='MON')
    time_open = models.TimeField(blank=True, null=True)
    time_close = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(
        'is closed?', blank=True, help_text='Check if location is closed on this day'
    )
    holiday_text = models.CharField(
        max_length=255,
        blank=True,
    )

    panels = [
        FieldPanel('day_of_week'),
        FieldPanel('time_open'),
        FieldPanel('time_close'),
        FieldPanel('closed'),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        open_time = self.opening_time.strftime('%H:%M') if self.time_open else '--'
        close_time = self.closing_time.strftime('%H:%M') if self.time_close else '--'

        return f'{self.day}: {open_time} - {close_time} {settings.TIME_ZONE}'


class LocationOperatingHours(Orderable, OperatingHours):
    """
    This model creates a relationship between the `OperatingHours` and
    `Location` objects. Unlike `BlogPersonRelationship` we do not include
    a `ForeignKey` to `OperatingHours` as we do not need that relationship
    (e.g. any `Location` open a certain day of the week).

    The `ParentalKey` is the minimum required to relate the two objects
    to one another. We use the `related_name` attribute of `ParentalKey` to
    access it from the `LocationPage` admin.
    """

    location = ParentalKey(
        'LocationPage', related_name='hours_of_operation', on_delete=models.CASCADE
    )


class LocationsListPage(Page):
    """
    List view page model for location objects.
    """

    about = RichTextField(blank=True, help_text='Text to describe this section')
    about_title = models.CharField(blank=True, max_length=255)
    about_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.',
    )

    # Max recent items to show on blog landing page
    max_recent = models.IntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name='Max recent',
        help_text='Max recent items to show on blog landing page',
    )

    # Only `LocationPage`` objects can be added underneath this list page
    subpage_types = ['LocationPage']

    # Allows children of this indexpage to be accessible via the indexpage
    # object on templates. We use this on the homepage to show featured
    # sections of the site and their child pages
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child
    # items, that are live, by the title alphabetical order.
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super().get_context(request)
        context['locations'] = LocationPage.objects.descendant_of(self).live().order_by('title')
        return context

    content_panels = Page.content_panels + [
        FieldPanel('about'),
        FieldPanel('about_title'),
        FieldPanel('about_image'),
        FieldPanel('max_recent'),
        InlinePanel('banner_images', label='Banner images'),
    ]


class LocationPage(Page):
    """
    Details for a specific location.
    """

    intro = models.TextField(help_text='Text to describe the page', blank=True, max_length=255)
    body = StreamField(
        BaseStreamBlock(),
        verbose_name='Page body',
        blank=True,
        use_json_field=True,
        help_text='Content for blog page using RichText format.',
    )
    street = models.CharField(blank=True, max_length=255)
    city = models.CharField(blank=True, max_length=255)
    state = models.CharField(blank=True, max_length=255)
    zip = models.CharField(
        blank=True,
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^\d{5}(?:-\d{4})?$',
                message='ZIP code as 5 digit or as ZIP+4 format',
                code='invalid_lat_long',
            ),
        ],
    )
    lat_long = models.CharField(
        max_length=36,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[
            RegexValidator(
                regex=r'^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$',
                message='Lat Long must be a comma-separated numeric lat and long',
                code='invalid_lat_long',
            ),
        ],
    )

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    # Fields to show to the editor in the admin view
    content_panels = [
        # FieldPanel("title"),
        FieldPanel('intro'),
        FieldPanel('body'),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('street'),
                        FieldPanel('city'),
                        FieldPanel('state'),
                        FieldPanel('zip'),
                    ]
                )
            ],
            'Mailing address',
        ),
        FieldPanel('lat_long'),
        InlinePanel('hours_of_operation', heading='Hours of Operation', label='Slot'),
        InlinePanel('gallery_images', label='Gallery images'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['LocationsListPage']
    subpage_types = ['LocationPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    def __str__(self):
        return f'Location - {self.title}'

    @property
    def operating_hours(self):
        return self.hours_of_operation.all()

    # Determines if the location is currently open. It is timezone naive
    def is_open(self):
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime('%a').upper()
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
        context = super().get_context(request)
        context['lat'] = self.lat_long.split(',')[0]
        context['long'] = self.lat_long.split(',')[1]
        context['google_map_api_key'] = settings.GOOGLE_MAP_API_KEY
        return context
