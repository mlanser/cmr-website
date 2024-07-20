from django import template

from base.models import Advert

register = template.Library()

# Advert snippets
@register.inclusion_tag('base/includes/adverts.html', takes_context=True)
def adverts(context):
    return {
        'adverts': Advert.objects.all(),
        'request': context['request'],
    }