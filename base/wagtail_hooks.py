from django.conf import settings
from django.utils.html import format_html

# from compressor.css import CssCompressor
from wagtail import hooks
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.userbar import AccessibilityItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from base.filters import RevisionFilterSetMixin
from base.models import Author, CopyrightText, FooterText, Person, Sponsor, Organizer


@hooks.register('insert_global_admin_css')
def import_fontawesome_stylesheet():
    elem = (
        f'<link rel="stylesheet" href="{settings.STATIC_URL}assets/css/fontawesome-all.min.css">'
    )
    return format_html(elem)


class CustomAccessibilityItem(AccessibilityItem):
    axe_run_only = None


@hooks.register("construct_wagtail_userbar")
def replace_userbar_accessibility_item(request, items):
    items[:] = [
        CustomAccessibilityItem() if isinstance(item, AccessibilityItem) else item
        for item in items
    ]


class PersonFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    class Meta:
        model = Person
        fields = {
            "job_title": ["icontains"],
            "live": ["exact"],
            "locked": ["exact"],
        }


class PersonViewSet(SnippetViewSet):
    # Instead of decorating the Person model class definition in models.py with
    # @register_snippet - which has Wagtail automatically generate an admin interface for this model - we can also provide our own
    # SnippetViewSet class which allows us to customize the admin interface for this snippet.
    # See the documentation for SnippetViewSet for more details
    # https://docs.wagtail.org/en/stable/reference/viewsets.html#snippetviewset
    model = Person
    menu_label = "People"  # ditch this to use verbose_name_plural from model
    icon = "group"  # change as required
    list_display = ("first_name", "last_name", "job_title", "thumb_image")
    list_export = ("first_name", "last_name", "job_title")
    filterset_class = PersonFilterSet


class AuthorFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    class Meta:
        model = Author
        fields = {
            "live": ["exact"],
            "locked": ["exact"],
        }


class AuthorViewSet(SnippetViewSet):
    model = Author
    menu_label = "Contributors"  # ditch this to use verbose_name_plural from model
    icon = "group"  # change as required
    list_display = ("name", "image")
    list_export = ("name")
    filterset_class = AuthorFilterSet


class OrganizerFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    class Meta:
        model = Organizer
        fields = {
            "live": ["exact"],
            "locked": ["exact"],
        }


class OrganizerViewSet(SnippetViewSet):
    model = Organizer
    menu_label = "Organizers"  # ditch this to use verbose_name_plural from model
    icon = "group"  # change as required
    list_display = ("name", "image")
    list_export = ("name")
    filterset_class = OrganizerFilterSet


class SponsorFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    class Meta:
        model = Sponsor
        fields = {
            "live": ["exact"],
            "locked": ["exact"],
        }


class SponsorViewSet(SnippetViewSet):
    model = Sponsor
    menu_label = "Sponsors"  # ditch this to use verbose_name_plural from model
    icon = "group"  # change as required
    list_display = ("name", "image")
    list_export = ("name")
    filterset_class = SponsorFilterSet


class CopyrightTextFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    class Meta:
        model = CopyrightText
        fields = {
            "live": ["exact"],
        }


class CopyrightTextViewSet(SnippetViewSet):
    model = CopyrightText
    search_fields = ("body",)
    filterset_class = CopyrightTextFilterSet


class FooterTextFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    class Meta:
        model = FooterText
        fields = {
            "live": ["exact"],
        }


class FooterTextViewSet(SnippetViewSet):
    model = FooterText
    search_fields = ("body",)
    filterset_class = FooterTextFilterSet


class DefaultSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = "Default Snippets"
    menu_icon = "utensils"  # change as required
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (
        AuthorViewSet, 
        OrganizerViewSet, 
        SponsorViewSet, 
        PersonViewSet, 
        CopyrightTextViewSet, 
        FooterTextViewSet
    )


# When using a SnippetViewSetGroup class to group several SnippetViewSet classes together,
# you only need to register the SnippetViewSetGroup class with Wagtail:
register_snippet(DefaultSnippetViewSetGroup)


# -----------------------------------------------------
# TODO: Review after installing `django-compressor` app
# -----------------------------------------------------
# @hooks.register("insert_global_admin_css")
# def import_fontawesome_stylesheet():
#     elem = '<link rel="stylesheet" type="text/x-scss" href="{}scss/fontawesome.scss">'.format(
#         settings.STATIC_URL
#     )
#     compressor = CssCompressor("css", content=elem)
#     output = ""
#     for s in compressor.hunks():
#         output += s
#     return format_html(output)
