# ... (existing code)
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from modelcluster.fields import ParentalKey

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel

from wagtail.models import Page, Orderable


from base.models import BannerSlide, EventItem


# -------------------------------------
#         C O R E   M O D E L S
# -------------------------------------
class HomePage(Page):
    # --------------------------------
    # Database fields
    # --------------------------------
    # Show banner section?
    show_banner = models.BooleanField(
        default=False,
        verbose_name='Show banner',
        help_text='Show banner on home page?',
    )

    # Show promoted content on home page?
    show_promo = models.BooleanField(
        default=False,
        verbose_name='Show promoted',
        help_text='Show promoted content on home page?',
    )
    promoted_page = models.ForeignKey(
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
    # Number of recent items to show on home page
    max_recent = models.IntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name='Max recent',
        help_text='Maximum number of recent items to show on home page',
    )

    # Show contact form and social media section?
    show_contact_info = models.BooleanField(
        default=False,
        verbose_name='Show contact info',
        help_text='Show content form and social media links on home page?',
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
            heading='Home page banner slides',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_promo'),
                PageChooserPanel('promoted_page', 'sections.SectionPage'),
            ],
            heading='Home page promoted content',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_happening'),
                FieldPanel('show_newsletter'),
            ],
            heading='Home page events',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_recent'),
                FieldPanel('max_recent'),
            ],
            heading='Home page recent content',
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_contact_info'),
                # PageChooserPanel('promoted_page', 'sections.SectionPage'),
            ],
            heading='Home page contact form, social media links, and visiting address and hours.',
        ),
    ]

    # promote_panels = []
    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    # parent_page_types = ['home.HomePage']
    subpage_types = ['sections.SectionMain', 'base.StandardPage']

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for the home page.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['is_home'] = True

        context['slides'] = []
        # if self.slide01:
        #     context['slides'].append(
        #         {'image': self.slide01, 'text': self.slide01_text, 'link': self.slide01_link}
        #     )
        # if self.slide02:
        #     context['slides'].append(
        #         {'image': self.slide02, 'text': self.slide02_text, 'link': self.slide02_link}
        #     )
        # if self.slide03:
        #     context['slides'].append(
        #         {'image': self.slide03, 'text': self.slide03_text, 'link': self.slide03_link}
        #     )
        # if self.slide04:
        #     context['slides'].append(
        #         {'image': self.slide04, 'text': self.slide04_text, 'link': self.slide04_link}
        #     )

        # sectionpages = self.get_children().live().order_by('-first_published_at')
        # context['sectionpages'] = sectionpages
        return context


# -------------------------------------
#     S U P P O R T   M O D E L S
# -------------------------------------
# HomePage Banner model
class HomePageBanner(Orderable, BannerSlide):
    slide01 = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='banner_slide01')
    slide02 = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='banner_slide02')
    slide03 = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='banner_slide03')
    slide04 = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='banner_slide04')


# HomePage Event model
class HomePageEvents(Orderable, EventItem):
    event01 = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='event_item01')
    event02 = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='event_item02')
