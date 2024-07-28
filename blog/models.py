from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, MultipleChooserPanel
from wagtail.fields import StreamField
from wagtail.models import Page, Orderable
from wagtail.search import index

from base.models import RelatedLink, GalleryImage, BannerImage
from base.blocks import BaseStreamBlock


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------
class BlogPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the BlogPage object and tags.

    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

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
    """
    Main/landing page for blogs.

    The blog main page is essentially the 'home page' for the blog section. It
    does not have any content of its own and only aggregates blog content.

    NOTE: We need to alter the page model's context to return the child page objects,
          the BlogPage objects, so that it works as an index page

    NOTE: We use `RoutablePageMixin` to allow for custom sub-URLs for the tag views
          defined above.
    """

    # ////////////////////////////////////////////////////////////

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
    subpage_types = ['blog.BlogPage', 'blog.BlogMDPage']

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


class BlogPage(Page):
    """
    Blog Page - RichText Format

    The blog page is the main page type used for general (story) content
    that is not tied to a specific section (i.e. CMR or NRHS).

    NOTE: This version is designed for content using RichText format.

    NOTE: We access the Person object with an inline panel that references the
          ParentalKey's `related_name` in `BlogPagePerson`.

          More docs:
          https://docs.wagtail.org/en/stable/topics/pages.html#inline-models
    """

    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Publish date', blank=True, null=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    intro = models.CharField(
        help_text='Text to describe this blog post', blank=True, max_length=255
    )
    body = StreamField(
        BaseStreamBlock(),
        verbose_name='Page body',
        blank=True,
        use_json_field=True,
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
        FieldPanel('date'),
        FieldPanel('tags'),
        FieldPanel('subtitle'),
        FieldPanel('intro'),
        FieldPanel('body'),
        MultipleChooserPanel(
            'blog_person_relationship',
            chooser_field_name='person',
            heading='Authors',
            label='Author',
            panels=None,
            min_num=1,
        ),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Related links'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    def authors(self):
        """
        Returns the BlogPage's related people. Again note that we are using
        the ParentalKey's related_name from the BlogPersonRelationship model
        to access these objects. This allows us to access the Person objects
        with a loop on the template. If we tried to access the blog_person_
        relationship directly we'd print `blog.BlogPersonRelationship.None`
        """
        # Only return authors that are not in draft
        return [
            n.person
            for n in self.blog_person_relationship.filter(person__live=True).select_related(
                'person'
            )
        ]

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f'{base_url}tags/{tag.slug}/'
        return tags

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


class BlogMDPage(Page):
    """
    -- DO NOT USE AS IS! --

    Blog Page - Markdown Format

    NOTE: This version is designed for content using Markdown format.

    TODO: NEED TO FIX THIS PAGE TYPE TO PROPERLY USE MARKDOWN FORMAT.
    """

    # --------------------------------
    # Database fields
    # --------------------------------
    date = models.DateField('Publish date', blank=True, null=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    intro = models.CharField(
        help_text='Text to describe this blog post', blank=True, max_length=255
    )
    # -- TODO: CHANGE TO MARKDOWN FIELD --
    body = StreamField(
        BaseStreamBlock(),
        verbose_name='Page body',
        blank=True,
        use_json_field=True,
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
        FieldPanel('date'),
        FieldPanel('tags'),
        FieldPanel('subtitle'),
        FieldPanel('intro'),
        FieldPanel('body'),
        MultipleChooserPanel(
            'blog_person_relationship',
            chooser_field_name='person',
            heading='Authors',
            label='Author',
            panels=None,
            min_num=1,
        ),
        InlinePanel('gallery_images', label='Gallery images'),
        InlinePanel('related_links', label='Related links'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    def authors(self):
        """
        Returns the BlogPage's related people. Again note that we are using
        the ParentalKey's related_name from the BlogPersonRelationship model
        to access these objects. This allows us to access the Person objects
        with a loop on the template. If we tried to access the blog_person_
        relationship directly we'd print `blog.BlogPersonRelationship.None`
        """
        # Only return authors that are not in draft
        return [
            n.person
            for n in self.blog_person_relationship.filter(person__live=True).select_related(
                'person'
            )
        ]

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f'{base_url}tags/{tag.slug}/'
        return tags

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
        context['is_markdown'] = False  # TODO: SWITCH TO `TRUE` ONCE MODEL IS FIXED

        return context

    def main_image(self):
        if gallery_item := self.gallery_images.first():
            return gallery_item.image
        else:
            return None


# ---------------------------------------------------------
#          M I S C   H E L P E R   C L A S S E S
# ---------------------------------------------------------
class BlogPerson(Orderable, models.Model):
    """
    This defines the relationship between a `Person` and `BlogPage` objects
    thus allowing people to be added to a blog page.

    This creates two-way relationship between `BlogPage` and `Person` using
    the `ParentalKey` and `ForeignKey` fields.
    """

    page = ParentalKey('Blog', related_name='blog_person_relationship', on_delete=models.CASCADE)
    person = models.ForeignKey(
        'base.Person', related_name='person_blog_relationship', on_delete=models.CASCADE
    )

    panels = [FieldPanel('person')]


class BlogMDPerson(Orderable, models.Model):
    page = ParentalKey('BlogMD', related_name='blog_person_relationship', on_delete=models.CASCADE)
    person = models.ForeignKey(
        'base.Person', related_name='person_blog_relationship', on_delete=models.CASCADE
    )

    panels = [FieldPanel('person')]


class BlogRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='related_links')


class BlogMDRelatedLink(Orderable, RelatedLink):
    page = ParentalKey(BlogMDPage, on_delete=models.CASCADE, related_name='related_links')


class BlogBannerImage(Orderable, BannerImage):
    page = ParentalKey(BlogMain, on_delete=models.CASCADE, related_name='banner_images')


class BlogGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')


class BlogMDGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(BlogMDPage, on_delete=models.CASCADE, related_name='gallery_images')
