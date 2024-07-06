from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from section_main.blocks import SectionMainStreamBlock


class SectionMainPage(Page):
    parent_page_types = ['home.HomePage']

    intro = StreamField(
        SectionMainStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Create a landing/main page for a section using RichText or Markdown.',
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        # Ensure context includes only published content, ordered by reverse-chron
        context = super().get_context(request)
        sectionpages = self.get_children().live().order_by('-first_published_at')
        context['sectionpages'] = sectionpages
        return context
