from django import template

from base.models import CopyrightText

register = template.Library()


@register.inclusion_tag('base/includes/copyright_text.html', takes_context=True)
def get_copyright_text(context):
    copyright_text = context.get('copyright_text', '')

    if not copyright_text:
        instance = CopyrightText.objects.filter(live=True).first()
        copyright_text = instance.body if instance else 'All rights reserved.'

    return {
        'copyright_text': copyright_text,
    }
