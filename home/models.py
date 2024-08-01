from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from modelcluster.fields import ParentalKey

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.models import Page, Orderable

from base.models import BannerImage
from blog.models import BlogPage, BlogMDPage
from sections.models import SectionPage, SectionMDPage


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------


# ---------------------------------------------------------
#           C O R E   P A G E   M O D E L S
# ---------------------------------------------------------
class HomePage(Page):
    """
    Home Page model

    The home page is specail in that it does not have any content of its own
    and only aggregates content from other sections.

    TODO:
    [ ] Add `faker` factory in `factories.py`
    """

    # --------------------------------
    # Database fields
    # --------------------------------
    # Show promoted content on home page?
    show_promo = models.BooleanField(
        default=False,
        verbose_name='Show promoted',
        help_text='Show promoted content on home page?',
    )
    promo_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promoted content',
        help_text='Select content to promote on home page',
    )

    # Show events and newsletter sign-up on home page?
    show_happening = models.BooleanField(
        default=False,
        verbose_name='Show events',
        help_text='Show upcoming events, shows, etc. on home page?',
    )
    show_newsletter = models.BooleanField(
        default=False,
        verbose_name='Show newsletter',
        help_text='Show newsletter sign-up on home page?',
    )

    # Show recent content on home page?
    show_recent = models.BooleanField(
        default=False,
        verbose_name='Show recent',
        help_text='Show recent content on home page?',
    )
    max_recent = models.IntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name='Max recent',
        help_text='Maximum recent items to show on home page',
    )

    # Show contact form and social media section?
    show_contact_info = models.BooleanField(
        default=True,
        verbose_name='Show contact info',
        help_text='Show content form and social media links on home page?',
    )

    # --------------------------------
    # Editor panels & search index configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        InlinePanel('banner_slides', label='Banner slides'),
        MultiFieldPanel(
            [
                FieldPanel('show_promo'),
                PageChooserPanel('promo_page', 'sections.SectionPage'),
            ],
            heading='Promoted content',
        ),
        InlinePanel('event_items', label='Event items'),
        MultiFieldPanel(
            [
                FieldPanel('show_happening'),
                FieldPanel('show_newsletter'),
            ],
            heading='Events and newsletter sign-up',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_recent'),
                FieldPanel('max_recent'),
            ],
            heading='Recent content',
        ),
        FieldPanel('show_contact_info'),
    ]

    # promote_panels = []
    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['wagtailcore.Page']
    subpage_types = [
        'sections.SectionMain',
        'blog.BlogMain',
        'base.StandardPage',
        'base.StandardMDPage',
    ]

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for the home page.'

    def __str__(self):
        return 'HomePage'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['is_home'] = True

        context['recent_posts'] = (
            self.get_descendents()
            .type(SectionPage, SectionMDPage, BlogPage, BlogMDPage)
            .live()
            .order_by('-first_published_at')
        )

        return context


# -------------------------------------
#     S U P P O R T   M O D E L S
# -------------------------------------
# Home Page Banner Slides
class BannerSlide(Orderable, BannerImage):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='banner_slides')


# HomePage Event model
class EventItem(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='event_items')
    event = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Promoted event',
        help_text='Select event item to promote on home page',
    )

    panels = [
        PageChooserPanel('event', 'sections.SectionPage'),
    ]
