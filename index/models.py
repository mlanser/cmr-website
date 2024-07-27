from wagtail.models import Page

from blog.models import BlogMDPage
from sections.models import SectionPage, SectionMDPage


class TagIndexPage(Page):
    # Parent page / subpage type rules
    parent_page_types = []
    subpage_types = []

    # Misc fields, helpers, and custom methods
    page_description = 'Use this content type for creating tag index pages.'

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        pages = BlogMDPage.objects.filter(tags__name=tag)
        pages += SectionPage.objects.filter(tags__name=tag)
        pages += SectionMDPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['pages'] = pages
        return context
