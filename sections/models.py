from django import forms
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from wagtail.search import index

from base.models import RelatedLink, GalleryImage, BannerImage
from base.blocks import BaseStreamBlock


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------
class SectionPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'SectionPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


class SectionMDPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'SectionMDPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


class EventPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'EventPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


class ShowPageTag(TaggedItemBase):
    content_object = ParentalKey('ShowPage', on_delete=models.CASCADE, related_name='tagged_items')


# ---------------------------------------------------------
#           C O R E   P A G E   M O D E L S
# ---------------------------------------------------------
# Section Main Page model
#
# NOTE: The section main page is essentially the 'home page' of a given section. It does
#       have its own content in the the 'About' box on the sidebar.
class SectionMain(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    # Show events on section landing page?
    show_happening = models.BooleanField(
        default=False,
        verbose_name='Show events',
        help_text='Show upcoming events, shows, etc. on landing page?',
    )

    # Number of recent items to show on section landing page
    max_recent = models.IntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name='Max recent',
        help_text='Max recent items to show on landing page',
    )

    # Show contact form and social media section?
    show_contact_info = models.BooleanField(
        editable=False,  # Locked with `default`` set to `False` to prevent editing
        default=False,
        verbose_name='Show contact info',
        help_text='Show content form and social media links on landing page?',
    )

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        InlinePanel('banner_images', label='Banner images'),
        MultiFieldPanel(
            [
                # This will have more fields in the future
                FieldPanel('show_happening'),
            ],
            heading='Section main page events',
        ),
        FieldPanel('max_recent'),
        # FieldPanel('show_contact_info'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['home.HomePage']
    subpage_types = ['sections.SectionSubMain', 'sections.SectionPage', 'sections.SectionMDPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for section landing page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_banner'] = True
        context['banner'] = {
            'image': self.banner_images.first().image if self.banner_images.first() else None,
            'text': self.banner_images.first().text if self.banner_images.first() else None,
        }

        section_pages = self.get_children().live().order_by('-first_published_at')

        if self.max_recent:
            context['recent_posts'] = section_pages[: (max(1, self.max_recent))]
        else:
            context['recent_posts'] = section_pages

        return context


class SectionSubMain(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    # Max recent items to show on sub-main page
    max_recent = models.IntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name='Max recent',
        help_text='Max recent items to show on sub-section landing page',
    )

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        InlinePanel('banner_images', label='Banner images'),
        FieldPanel('max_recent'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['sections.SectionMain']
    subpage_types = ['sections.SectionPage', 'sections.SectionMDPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for sub-section landing page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_banner'] = True
        context['banner'] = {
            'image': self.banner_images.first().image if self.banner_images.first() else None,
            'text': self.banner_images.first().text if self.banner_images.first() else None,
        }

        section_pages = self.get_children().live().order_by('-first_published_at')
        context['show_promo'] = True
        context['promo'] = section_pages.first()

        if self.max_recent:
            context['recent_posts'] = section_pages[1 : (max(2, self.max_recent + 1))]
        else:
            context['recent_posts'] = section_pages[1:]

        return context


# Section Page model - Markdown Format
#
# The section page is the main page type used for content (e.g. projects,
# exhibits, etc.) in all sections.
#
# NOTE: This version is designed for content using Markdown format.
#
class SectionMDPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=SectionMDPageTag, blank=True)
    intro = models.CharField(max_length=255)
    body = StreamField(
        BaseStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Content for section page using Markdown format.',
    )

    # --------------------------------
    # Search index configuration
    # --------------------------------
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
        index.FilterField('date'),
    ]

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('date'),
                FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
                FieldPanel('tags'),
            ],
            heading='Content meta data',
        ),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Related links'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['sections.SectionMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for common page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# Section Page model - RichText Format
#
# The section page is the main page type used for content (e.g. projects,
# exhibits, etc.) in all sections.
#
# NOTE: This version is designed for content using RichText format.
#
class SectionPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=SectionPageTag, blank=True)
    intro = models.CharField(max_length=255)
    body = RichTextField(
        blank=True,
        help_text='Content for section page using RichText format.',
    )

    # --------------------------------
    # Search index configuration
    # --------------------------------
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
        index.FilterField('date'),
    ]

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('date'),
                FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
                FieldPanel('tags'),
            ],
            heading='Content meta data',
        ),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Related links'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['sections.SectionMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for common page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# Event Page model - RichText Format
#
# The event page is the main page type used for describing events and
# related information in all sections.
#
# NOTE: This page type also relies on displaying data in sidebar
#       tiles (e.g. 'Location', etc.).
#
class EventPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    tags = ClusterTaggableManager(through=EventPageTag, blank=True)
    intro = models.CharField(max_length=255)
    body = RichTextField(
        blank=True,
        help_text='Content for event page using RichText format.',
    )

    event_date = models.DateField('Event date')
    event_start_time = models.TimeField('Event start time')
    event_end_time = models.TimeField('Event end time')

    public = models.BooleanField(
        default=False,
        verbose_name='Public event',
        help_text='Is this a public event?',
    )

    organizers = ParentalManyToManyField('base.Organizer', blank=True)
    location = ParentalManyToManyField('base.Location', blank=True)
    sponsors = ParentalManyToManyField('base.Sponsor', blank=True)

    # --------------------------------
    # Search index configuration
    # --------------------------------
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
        index.FilterField('date'),
    ]

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('date'),
                FieldPanel('tags'),
            ],
            heading='Content meta data',
        ),
        MultiFieldPanel(
            [
                FieldPanel('event_date'),
                FieldPanel('event_start_time'),
                FieldPanel('event_end_time'),
                FieldPanel('public'),
                FieldPanel('organizers', widget=forms.CheckboxSelectMultiple),
                FieldPanel('location', widget=forms.RadioSelect),
                FieldPanel('sponsors', widget=forms.CheckboxSelectMultiple),
            ],
            heading='Event information',
        ),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Related links'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['sections.SectionMain', 'sections.SectionSubMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for event information.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# Show Page model - RichText Format
#
# The event page is the main page type used for describing events and
# related information in all sections.
#
# NOTE: This page type also relies on displaying data in sidebar
#       tiles (e.g. 'Location', etc.).
#
class ShowPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    tags = ClusterTaggableManager(through=EventPageTag, blank=True)
    intro = models.CharField(max_length=255)
    body = RichTextField(
        blank=True,
        help_text='Content for event page using RichText format.',
    )

    show_start_date = models.DateField('Show start date')
    show_end_date = models.DateField('Show end date')
    show_start_time = models.TimeField('Show start time')
    show_end_time = models.TimeField('Show end time')

    public = models.BooleanField(
        default=True,
        verbose_name='Public event',
        help_text='Is this a public event?',
    )

    organizers = ParentalManyToManyField('base.Organizer', blank=True)
    location = ParentalManyToManyField('base.Location', blank=True)
    sponsors = ParentalManyToManyField('base.Sponsor', blank=True)

    # --------------------------------
    # Search index configuration
    # --------------------------------
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
        index.FilterField('date'),
    ]

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('date'),
                FieldPanel('tags'),
            ],
            heading='Content meta data',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_start_date'),
                FieldPanel('show_end_date'),
                FieldPanel('show_start_time'),
                FieldPanel('show_end_time'),
                FieldPanel('public'),
                FieldPanel('organizers', widget=forms.CheckboxSelectMultiple),
                FieldPanel('location', widget=forms.RadioSelect),
                FieldPanel('sponsors', widget=forms.CheckboxSelectMultiple),
            ],
            heading='Show information',
        ),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Related links'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['sections.SectionMain', 'sections.SectionSubMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for show information.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# ---------------------------------------------------------
#          M I S C   H E L P E R   C L A S S E S
# ---------------------------------------------------------
# Related Links
class SectionPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(SectionPage, on_delete=models.CASCADE, related_name='related_links')


class SectionMDPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(SectionMDPage, on_delete=models.CASCADE, related_name='related_links')


class EventPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(EventPage, on_delete=models.CASCADE, related_name='related_links')


class ShowPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(ShowPage, on_delete=models.CASCADE, related_name='related_links')


# Banner & Gallery Images
class SectionMainBannerImage(Orderable, BannerImage):
    page = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='banner_images')


class SectionSubMainBannerImage(Orderable, BannerImage):
    page = ParentalKey(SectionSubMain, on_delete=models.CASCADE, related_name='banner_images')


class SectionPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(SectionPage, on_delete=models.CASCADE, related_name='gallery_images')


class SectionMDPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(SectionMDPage, on_delete=models.CASCADE, related_name='gallery_images')


class EventPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(EventPage, on_delete=models.CASCADE, related_name='gallery_images')


class ShowPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(ShowPage, on_delete=models.CASCADE, related_name='gallery_images')
