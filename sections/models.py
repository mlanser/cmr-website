from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.contrib.routable_page.models import route
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.search import index

from base.models import RelatedLink, GalleryImage, BannerImage


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------
class SectionPageTag(TaggedItemBase):
    """
    Model to create a many-to-many relationship between
    the `SectionPage` objects and tags.
    """

    content_object = ParentalKey(
        'sections.SectionPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


class EventPageTag(TaggedItemBase):
    """
    Model to create a many-to-many relationship between
    the `EventPage` objects and tags.
    """

    content_object = ParentalKey(
        'sections.EventPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


class ShowPageTag(TaggedItemBase):
    """
    Model to create a many-to-many relationship between
    the `ShowPage` objects and tags.
    """

    content_object = ParentalKey(
        'sections.ShowPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


# ---------------------------------------------------------
#           C O R E   P A G E   M O D E L S
# ---------------------------------------------------------
# Section Main Page model
#
# NOTE: The section main page is essentially the 'home page' of a given section. It does
#       have its own content in the the 'About' box on the sidebar.
class SectionMain(Page):
    """
    Main/landing page for main sections.

    The section main page is essentially the 'home page' for core sections. It
    does not have any content of its own and only aggregates section content.

    NOTE: We need to alter the page model's context to return the child page objects
          so that it works as an index page

    NOTE: We use `RoutablePageMixin` to allow for custom sub-URLs for the tag views
          defined above.

    TODO:
    TODO:
    [ ] Add support for Markdown constent (e.g. `SectionMDPage`, etc.)
    [ ] Add `faker` factory in `factories.py`
    """

    # --------------------------------
    # Database fields
    # --------------------------------
    # Show events on section landing page?
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
        FieldPanel('about'),
        FieldPanel('about_title'),
        FieldPanel('about_image'),
        MultiFieldPanel(
            [
                # This will have more fields in the future
                FieldPanel('show_happening'),
            ],
            heading='Section main page events',
        ),
        FieldPanel('max_recent'),
        InlinePanel('banner_images', label='Banner images'),
        # FieldPanel('show_contact_info'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['home.HomePage']
    subpage_types = ['sections.SectionSubMain', 'sections.SectionPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for section landing page content.'

    def __str__(self):
        return f'SectionMain - {self.title}'

    # Method to access children of the section landing page (i.e. `SectionPage`
    # objects).
    def children(self):
        return self.get_children().specific().live()

    # This defines a custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the BlogIndexPage.
    # More information on RoutablePages is at
    # https://docs.wagtail.org/en/stable/reference/contrib/routablepage.html
    @route(r'^tags/$', name='tag_archive')
    @route(r'^tags/([\w-]+)/$', name='tag_archive')
    def tag_archive(self, request, tag=None):
        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = f'There is no content tagged with "{tag}"'
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {
            'self': self,
            'tag': tag,
            'posts': posts,
            'header': f'Content tagged with: {tag}',
        }
        # TODO: Check if this is the correct template
        return render(request, 'sections/section_main.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child SectionPage objects for this SectionMain page.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = SectionPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            # Not using `tags.append()` as we do not want a list of lists
            tags += post.get_tags
        return sorted(set(tags))

    # Override default context to list all child items
    #
    # Docs:
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
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
    subpage_types = ['sections.SectionPage']

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
    # authors = ParentalManyToManyField('base.Author', blank=True)
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
                # FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
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

    # location = ParentalManyToManyField('base.Location', blank=True)

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
                # FieldPanel('location', widget=forms.RadioSelect),
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

    # location = ParentalManyToManyField('base.Location', blank=True)

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
                # FieldPanel('location', widget=forms.RadioSelect),
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


class EventPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(EventPage, on_delete=models.CASCADE, related_name='gallery_images')


class ShowPageGalleryImage(Orderable, GalleryImage):
    page = ParentalKey(ShowPage, on_delete=models.CASCADE, related_name='gallery_images')
