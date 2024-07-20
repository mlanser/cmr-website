from django import forms
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel

from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable


from wagtail.search import index

from base.models import BannerSlide, EventItem
from sections.blocks import SectionPageStreamBlock


# Section Main Page model
#
# NOTE: The section main page is essentially the 'home page' of a given section. It does
#       have its own content in the the 'About' box on the sidebar.
class SectionMain(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    # Show banner section?
    show_banner = models.BooleanField(
        default=False,
        verbose_name='Show banner',
        help_text='Show banner on section landing page?',
    )

    # Show promoted content on section landing page?
    show_promo = models.BooleanField(
        default=False,
        verbose_name='Show promoted',
        help_text='Show promoted content on section landing page?',
    )
    promoted_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promoted content',
        help_text='Select content to promote on section landing page',
    )

    # Show events on section landing page?
    show_happening = models.BooleanField(
        default=False,
        verbose_name='Show events',
        help_text='Show upcoming events, shows, etc. on section landing page?',
    )

    # Show recent content on section landing page?
    show_recent = models.BooleanField(
        default=False,
        verbose_name='Show recent',
        help_text='Show recent content on section landing page?',
    )
    # Number of recent items to show on section landing page
    max_recent = models.IntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name='Max recent',
        help_text='Maximum number of recent items to show on section landing page',
    )

    # Show contact form and social media section?
    show_contact_info = models.BooleanField(
        default=False,
        verbose_name='Show contact info',
        help_text='Show content form and social media links on section landing page?',
    )

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('show_banner'),
                # PageChooserPanel('promoted_page', 'sections.SectionPage'),
            ],
            heading='Section main page banner slides',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_promo'),
                PageChooserPanel('promoted_page', 'sections.SectionPage'),
            ],
            heading='Section main page promoted content',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_happening'),
            ],
            heading='Section main page events',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_recent'),
                FieldPanel('max_recent'),
            ],
            heading='Section main page recent content',
        ),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    # parent_page_types = ['home.HomePage']
    subpage_types = ['sections.SectionPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for main section/landing page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['DEBUG'] = 'DEBUG'  # Placeholder for custom context variables

        sectionpages = self.get_children().live().order_by('-first_published_at')
        context['sectionpages'] = sectionpages
        return context

    # def main_image(self):
    #     return self.feed_image or None


# Section Main Banner model
class SectionMainBanner(Orderable, BannerSlide):
    slide01 = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='banner_slide01')
    slide02 = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='banner_slide02')
    slide03 = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='banner_slide03')
    slide04 = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='banner_slide04')


# Section Main Event model
class SectionMainEvents(Orderable, EventItem):
    event01 = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='event_item01')
    event02 = ParentalKey(SectionMain, on_delete=models.CASCADE, related_name='event_item02')


class SectionPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'SectionPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


# Section Page model - Markdown Format
#
# The section page is the main page type used for content (e.g. events,
# shows, projects, exhibits, blog posts, etc.) in all sections.
#
# NOTE: This version is designed for content using Markdown format.
#
class SectionMDPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=SectionPageTag, blank=True)
    intro = models.CharField(max_length=250)
    body = StreamField(
        SectionPageStreamBlock(),
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
            heading='Section information',
        ),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Relaterd links'),
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

        # Add extra variables and return updated context
        context['show_meta'] = True
        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# Section Page model - RichText Format
#
# The section page is the main page type used for content (e.g. events,
# shows, projects, exhibits, blog posts, etc.) in all sections.
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
    intro = models.CharField(max_length=250)
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
            heading='Section information',
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

        # Add extra variables and return updated context
        context['show_meta'] = True
        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return {
                'image': gallery_item.image,
                'caption': gallery_item.caption,
                'credit_text': gallery_item.credit_text,
                'credit_url': gallery_item.credit_url,
            }
        else:
            return None


class SectionPageRelatedLink(Orderable):
    page = ParentalKey(SectionPage, on_delete=models.CASCADE, related_name='related_links')
    name = models.CharField(max_length=250)
    url = models.URLField()

    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
    ]


class SectionMDPageRelatedLink(Orderable):
    page = ParentalKey(SectionMDPage, on_delete=models.CASCADE, related_name='related_links')
    name = models.CharField(max_length=250)
    url = models.URLField()

    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
    ]


class SectionPageGalleryImage(Orderable):
    page = ParentalKey(SectionPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')
    caption = models.CharField(blank=True, max_length=250)
    credit_text = models.CharField(blank=True, max_length=250)
    credit_url = models.URLField(blank=True)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),  # ALT text
        FieldPanel('credit_text'),
        FieldPanel('credit_url'),
    ]


class SectionMDPageGalleryImage(Orderable):
    page = ParentalKey(SectionMDPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')
    caption = models.CharField(blank=True, max_length=250)
    credit_text = models.CharField(blank=True, max_length=250)
    credit_url = models.URLField(blank=True)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),  # ALT text
        FieldPanel('credit_text'),
        FieldPanel('credit_url'),
    ]


class SectionTagIndexPage(Page):
    # Parent page / subpage type rules
    parent_page_types = []
    subpage_types = []

    # Misc fields, helpers, and custom methods
    page_description = 'Use this content type for creating tag index pages.'

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        sectionpages = SectionPage.objects.filter(tags__name=tag) + SectionMDPage.objects.filter(
            tags__name=tag
        )

        # Update template context
        context = super().get_context(request)
        context['sectionpages'] = sectionpages
        return context
