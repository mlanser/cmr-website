from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from base.models import Advert


class AdvertViewSet(SnippetViewSet):
    model = Advert

    panels = [
        FieldPanel('url'),
        FieldPanel('text'),
        FieldPanel('image'),
    ]


# Instead of using @register_snippet as a decorator on the model class,
# register the snippet using register_snippet as a function and pass in
# the custom SnippetViewSet subclass.
register_snippet(AdvertViewSet)
