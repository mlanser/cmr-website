from django.apps import AppConfig


class SectionMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'section_main'


class SectionPageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'section_page'
