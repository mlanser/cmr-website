from django.conf import settings
from django.utils.html import format_html

# from compressor.css import CssCompressor
from wagtail import hooks


@hooks.register('insert_global_admin_css')
def import_fontawesome_stylesheet():
    elem = (
        f'<link rel="stylesheet" href="{settings.STATIC_URL}assets/css/fontawesome-all.min.css">'
    )
    return format_html(elem)


# -----------------------------------------------------
# TODO: REview after installing `django-compressor` app
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
