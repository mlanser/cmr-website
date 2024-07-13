# sourcery skip: use-fstring-for-concatenation
"""
URL configuration for CMR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView


# from search import views as search_views

urlpatterns = [
    # path('django-admin/', admin.site.urls),
    # path('admin/', include(wagtailadmin_urls)),
    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    re_path(
        r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$',
        ServeView.as_view(),
        name='wagtailimages_serve',
    ),
    # path("search/", search_views.search, name="search"),
    path('sitemap.xml', sitemap),
    # path("api/v2/", api_router.urls),
    # Optional URL for including your own vanilla Django urls/views
    # re_path('my_app', include('my_app.urls')),
    # re_path('layouts/', include('cmr_layouts.urls')),
    # re_path('members/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),  # Required by `allauth`
]

# Following is for local DEV in DEBUG mode only!
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView
    from django.views.generic.base import RedirectView

    # For DEV only. For PROD, use a web server like Nginx or Apache to serve static files
    # https://docs.djangoproject.com/en/4.2/howto/static-files/
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        path(
            'favicon.ico',
            RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico'),
            name='favicon',
        ),
        # Optional URL for including your own vanilla Django urls/views
        re_path(
            'theme-sctn-main/',
            TemplateView.as_view(template_name='debug/theme-sctn-main.html'),
            name='theme_sctn_main',
        ),
        re_path(
            'theme-sctn-page/',
            TemplateView.as_view(template_name='debug/theme-sctn-page.html'),
            name='theme_sctn_page',
        ),
        re_path(
            'theme-elements/',
            TemplateView.as_view(template_name='debug/theme-elements.html'),
            name='theme_elements',
        ),
        re_path(
            'theme-home/',
            TemplateView.as_view(template_name='debug/theme-home.html'),
            name='theme_home',
        ),
    ]

    # Required by `django-debug-toolbar`
    if not settings.TESTING:
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
            path('test404/', TemplateView.as_view(template_name='404.html')),
            path('test500/', TemplateView.as_view(template_name='500.html')),
        ]

# For anything not caught by a more specific rule above, hand over to
# Wagtail's serving mechanism
urlpatterns += [
    path('', include(wagtail_urls)),
]
