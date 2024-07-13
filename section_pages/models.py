from django import forms
from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from section_pages.blocks import SectionPagesStreamBlock


class SectionPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'SectionPage', related_name='tagged_items', on_delete=models.CASCADE
    )


class SectionPage(Page):
    # Database fields
    date = models.DateField('Post date')
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=SectionPageTag, blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    intro = models.CharField(max_length=250)
    body = StreamField(
        SectionPagesStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Create a landing/main page for a section using Markdown.',
    )

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
        index.FilterField('date'),
    ]

    # Editor panels configuration
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
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
        FieldPanel('feed_image'),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['section_main.SectionMainPage']
    subpage_types = []

    # Misc fields, helpers, and custom methods
    page_description = 'Use this content type for common page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['showMeta'] = True
        context['DEBUG'] = 'DEBUG'  # Placeholder for custom context variables
        return context

    def main_image(self):
        if self.feed_image:
            return self.feed_image
        elif gallery_item := self.gallery_images.first():
            return gallery_item.image
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


class SectionPageGalleryImage(Orderable):
    page = ParentalKey(SectionPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
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
        sectionpages = SectionPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['sectionpages'] = sectionpages
        return context
