from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    MultipleChooserPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from wagtail.search import index

from base.models import RelatedLink, GalleryImage, BannerImage, SiteSettings
from base.blocks import BaseStreamBlock


# ---------------------------------------------------------
#               M I S C   C O N S T A N T S
# ---------------------------------------------------------
PAGINATION_MIN_PAGES = 7
PAGINATION_BOUNDARY = 3


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------
class BlogPageTag(TaggedItemBase):
    """
    Model to create a many-to-many relationship between
    the `BlogPage` objects and tags.

    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

    content_object = ParentalKey(
        'blog.BlogPage', on_delete=models.CASCADE, related_name='tagged_items'
    )


# ---------------------------------------------------------
#           C O R E   P A G E   M O D E L S
# ---------------------------------------------------------
class BlogMain(RoutablePageMixin, Page):
    """
    Main/landing page for blogs.

    The blog main page is essentially the 'home page' for the blog section. It
    does not have any content of its own and only aggregates blog content.

    NOTE: We need to alter the page model's context to return the child page objects,
          the BlogPage objects, so that it works as an index page

    NOTE: We use `RoutablePageMixin` to allow for custom sub-URLs for the tag views
          defined above.

    TODO:
    [ ] Add support for Markdown constent (e.g. `BlogMDPage`, etc.)
    [ ] Add `faker` factory in `factories.py`
    """

    # --------------------------------
    # Database fields
    # --------------------------------
    # Text to be displayed on the sidebar in the `About` tile.
    about_title = models.CharField(blank=True, max_length=255)
    about_desc = RichTextField(blank=True, help_text='Text to describe this section')
    about_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.',
    )
    about_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Optional link',
        help_text='Select page with additional related content',
    )

    show_tag_cloud = models.BooleanField(
        default=True,
        verbose_name='Show tag cloud',
        help_text='Show tag cloud tile on sidebar?',
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

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('about_title'),
                FieldPanel('about_desc'),
                FieldPanel('about_image'),
                PageChooserPanel('about_link'),
            ],
            heading="Sidebar 'About' tile",
        ),
        FieldPanel('show_tag_cloud'),
        FieldPanel('max_recent'),
        InlinePanel('banner_images', label='Banner images'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['home.HomePage']
    subpage_types = ['blog.BlogPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for the blog landing page.'

    def __str__(self):
        return f'BlogMain - {self.title}'

    # Method to access (published) children of the blog landing
    # page (i.e. `BlogPage`objects) soterd by date
    def get_published_posts(self, tag=None):
        if tag:
            return (
                BlogPage.objects.live()
                .descendant_of(self)
                .filter(tags=tag)
                .order_by('-first_published_at')
                .specific()
            )
            # return self.get_children().type(BlogPage).live().filter(tags=tag).order_by('-first_published_at').specific()
        else:
            return (
                BlogPage.objects.live()
                .descendant_of(self)
                .order_by('-first_published_at')
                .specific()
            )
            # return self.get_children().type(BlogPage).live().order_by('-first_published_at').specific()
        # return self.get_children().specific().live()

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
                msg = f'There is no blog content tagged with "{tag}"'
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        # Get all blog pages filtered by tag
        all_posts = self.get_published_posts(tag=tag)
        paginator = self.get_paginator(all_posts, all=True)

        header = f"Blog posts tagged with: '{tag}'"
        context = {
            'self': self,
            'show_banner': True,
            'banner': self.banner_images.first() or None,
            'tag': tag,
            'tag_list': self.get_tags_for_published_posts(),
            'show_promo': False,
            'promo': None,
            'header': header,
            'posts': self.get_paginated_posts(paginator, request),
            'paginator': self.get_paginator_items(paginator, request),
        }

        # TODO: Check if this is the correct template
        return render(request, 'blog/blog_main.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the list of Tags for all child posts of this BlogPage.
    def get_tags_for_published_posts(self):
        tags = []
        for post in self.get_published_posts():
            # We do NOT use `tags.append()` as we
            # don't want a list of lists
            tags += post.get_tags
        return sorted(set(tags))

    def get_paginator(self, all_posts, all=False):
        return (
            Paginator(all_posts[1:], self.max_recent)
            if (len(all_posts) > 1 and not all)
            else Paginator(all_posts, self.max_recent)
        )

    def get_paginated_posts(self, paginator, request):
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return posts

    def get_paginator_items(self, paginator, request):
        """
        If we have more pagination pages than `max_pages`, then we'll show
        ellipsis in the middle of the paginator row.

        Here we create a list that can be parsed in the pagination templates,
        and we use `0` as a placeholder for the ellipsis.
        """

        # Max items/page icons to show in paginator.
        site_settings = SiteSettings.for_request(request)
        max_pages = max(PAGINATION_MIN_PAGES, int(site_settings.pagination_max_pages))

        # Can we comfortably display all items?
        if paginator.num_pages <= max_pages:
            return range(1, paginator.num_pages + 1)

        # If we have too many paginator pages, then we'll need to figure where to
        # show page numbers and where to show ellipsis.
        lower_boundary = PAGINATION_BOUNDARY
        upper_boundary = paginator.num_pages - PAGINATION_BOUNDARY + 1
        ellipse = True

        page = request.GET.get('page')
        page = min(max(1, int(page)), paginator.num_pages)

        items = []

        for i in range(1, paginator.num_pages + 1):
            if i <= lower_boundary:
                items.append(i)
            elif i == (lower_boundary + 1) and i == page:
                items.append(i)
            elif i == (upper_boundary - 1) and i == page:
                items.append(i)
            elif i >= upper_boundary:
                items.append(i)
            elif i == page:
                items.append(i)
                ellipse = True
            else:
                if ellipse:
                    items.append(0)
                ellipse = False

        return items

    # Override default context to list all child items
    #
    # Docs:
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_banner'] = True
        context['banner'] = self.banner_images.first() or None

        context['tag_list'] = self.get_tags_for_published_posts()

        # Get all blog pages and sort by date
        all_posts = self.get_published_posts()

        context['show_promo'] = len(all_posts) >= 1
        context['promo'] = all_posts.first() or None
        context['header'] = (
            'Recent blog posts' if len(all_posts) >= 1 else 'No additional posts found'
        )

        # Exclude first item and get up to max which is used as 'promo' item
        paginator = self.get_paginator(all_posts)

        context['posts'] = self.get_paginated_posts(paginator, request)
        context['paginator'] = self.get_paginator_items(paginator, request)

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

    [ ] TODO: Add `faker` factory in `factories.py`
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

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['blog.BlogMain']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for common blog page content.'

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

    def __str__(self):
        return f'BlogPage - {self.title}'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        context['show_intro'] = False
        context['is_richtext'] = True

        context['gallery'] = self.gallery_images.all()

        return context

    def main_image(self):
        # return gallery_item if (gallery_item := self.gallery_images.first()) else None
        return self.gallery_images.first() or None


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

    page = ParentalKey(
        'blog.BlogPage', related_name='blog_person_relationship', on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'base.Person', related_name='person_blog_relationship', on_delete=models.CASCADE
    )

    panels = [FieldPanel('person')]


class BlogRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('blog.BlogPage', on_delete=models.CASCADE, related_name='related_links')


class BlogBannerImage(Orderable, BannerImage):
    page = ParentalKey('blog.BlogMain', on_delete=models.CASCADE, related_name='banner_images')


class BlogGalleryImage(Orderable, GalleryImage):
    page = ParentalKey('blog.BlogPage', on_delete=models.CASCADE, related_name='gallery_images')
