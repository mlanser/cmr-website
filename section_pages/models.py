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


# TODO: Remove this class if not needed
# class SectionIndexPage(Page):
#     intro = RichTextField(blank=True)

#     def get_context(self, request):
#         # Ensure context includes only published posts, ordered by reverse-chron
#         context = super().get_context(request)
#         sectionpages = self.get_children().live().order_by('-first_published_at')
#         context['sectionpages'] = sectionpages
#         return context

#     content_panels = Page.content_panels + [FieldPanel('intro')]


class SectionPage(Page):
    parent_page_types = ['section_main.SectionMainPage']

    date = models.DateField('Post date')
    intro = models.CharField(max_length=250)
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=SectionPageTag, blank=True)

    # body = RichTextField(blank=True)
    body = StreamField(
        SectionPagesStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Create a landing/main page for a section using RichText or Markdown.',
    )

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

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


class SectionPageGalleryImage(Orderable):
    page = ParentalKey(SectionPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]


class SectionTagIndexPage(Page):
    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        sectionpages = SectionPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['sectionpages'] = sectionpages
        return context
