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
from sections.blocks import SectionPageStreamBlock


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', on_delete=models.CASCADE, related_name='tagged_items')


class BlogMDPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogMDPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


# ---------------------------------------------------------
#           C O R E   P A G E   M O D E L S
# ---------------------------------------------------------
# Blog Main Page model
#
# NOTE: The blog main page is essentially the 'home page' for the blog section. It
#       does not have any content of its own and only aggregates blog content.
class BlogMain(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
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
    parent_page_types = ['home.HomePage']
    subpage_types = ['blog.BlogMDPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for the blog landing page.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_banner'] = True
        context['banner'] = {
            'image': self.banner_images.first().image if self.banner_images.first() else None,
            'text': self.banner_images.first().text if self.banner_images.first() else None,
        }

        blog_pages = self.get_children().live().order_by('-first_published_at')
        context['show_promo'] = True
        context['promo'] = blog_pages.first()

        # Exclude first item and get up to max which is used as 'promo' item
        if self.max_recent > 1:
            context['recent_posts'] = blog_pages[1 : (max(2, self.max_recent + 1))]
        else:
            context['recent_posts'] = blog_pages[1:]

        return context


# Blog Page model - Markdown Format
#
# The blog page is the main page type used for general (story) content
# that is not tied to a specific section (i.e. CMR or NRHS).
#
# NOTE: This version is designed for content using Markdown format.
#
class BlogMDPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=BlogMDPageTag, blank=True)
    intro = models.CharField(max_length=255)
    body = StreamField(
        SectionPageStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Content for blog page using Markdown format.',
    )

    # --------------------------------
    # Search index configuration
    # --------------------------------
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
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
    parent_page_types = ['blog.BlogMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for common blog page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        context['show_intro'] = False
        context['is_markdown'] = True

        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# Blog Page model - RichText Format
#
# The blog page is the main page type used for general (story) content
# that is not tied to a specific section (i.e. CMR or NRHS).
#
# NOTE: This version is designed for content using RichText format.
#
class BlogPage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Post date')
    authors = ParentalManyToManyField('base.Author', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    intro = models.CharField(max_length=255)
    body = RichTextField(
        blank=True,
        help_text='Content for blog page using RichText format.',
    )

    # --------------------------------
    # Search index configuration
    # --------------------------------
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
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
    parent_page_types = ['blog.BlogMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for common blog page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        context['show_intro'] = False
        context['is_richtext'] = True

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
class BlogPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='related_links')


class BlogMDPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(BlogMDPage, on_delete=models.CASCADE, related_name='related_links')


# Banner & Gallery Images
class BlogMainBannerImage(Orderable, BannerImage):
    page = ParentalKey(BlogMain, on_delete=models.CASCADE, related_name='banner_images')


class BlogPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')


class BlogMDPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(BlogMDPage, on_delete=models.CASCADE, related_name='gallery_images')
