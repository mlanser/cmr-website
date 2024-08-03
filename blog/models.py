from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, MultipleChooserPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from wagtail.search import index

from base.models import RelatedLink, GalleryImage, BannerImage
from base.blocks import BaseStreamBlock


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

    # --------------------------------
    # Editor panels configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        FieldPanel('about'),
        FieldPanel('about_title'),
        FieldPanel('about_image'),
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

    # Method to access children of the blog landing page (i.e. `BlogPage`
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
                msg = f'There is no blog content tagged with "{tag}"'
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {
            'self': self,
            'tag': tag,
            'posts': posts,
            'header': f'Blog posts tagged with: {tag}',
        }
        # TODO: Check if this is the correct template
        return render(request, 'blog/blog_main.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child BlogPage objects for this BlogMain page.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = BlogPage.objects.live().descendant_of(self)
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

        # blog_pages = BlogPage.objects.descendant_of(self).live().order_by('-date_published')
        blog_pages = self.get_children().live().order_by('-first_published_at')
        context['show_promo'] = True
        context['promo'] = blog_pages.first()
        context['header'] = 'Recent blog posts'

        # Exclude first item and get up to max which is used as 'promo' item
        if self.max_recent > 1:
            context['posts'] = blog_pages[1 : (max(2, self.max_recent + 1))]
        else:
            context['posts'] = blog_pages[1:]

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
