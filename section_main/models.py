from django.db import models


from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from section_main.blocks import SectionMainStreamBlock


class SectionMainPage(Page):
    # Database fields
    feed_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    body = StreamField(
        SectionMainStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Create a landing/main page for a section using Markdown.',
    )

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
        FieldPanel('feed_image'),
    ]

    # Parent page / subpage type rules
    # parent_page_types = ['home.HomePage']
    subpage_types = ['section_pages.SectionPage']

    # Misc fields, helpers, and custom methods
    page_description = 'Use this content type for main section/landing page content.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['showMeta'] = False
        context['showContact'] = True
        context['DEBUG'] = 'DEBUG'  # Placeholder for custom context variables

        sectionpages = self.get_children().live().order_by('-first_published_at')
        context['sectionpages'] = sectionpages
        return context

    def main_image(self):
        return self.feed_image or None
