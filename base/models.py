from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PublishingPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, PreviewableMixin, RevisionMixin, TranslatableMixin
from wagtail.snippets.models import register_snippet


@register_setting
class ContactSettings(BaseGenericSetting):
    email_cmr = models.EmailField(
        help_text='Email address for CMR', verbose_name='CMR Email', blank=True
    )
    email_nrhs = models.EmailField(
        help_text='Email address for NRHS', verbose_name='NRHS Email', blank=True
    )
    phone_cmr = PhoneNumberField(
        help_text='Phone number for CMR', verbose_name='CMR Phone', blank=True
    )
    phone_nrhs = PhoneNumberField(
        help_text='Phone number for NRHS', verbose_name='NRHS Phone', blank=True
    )
    address_cmr = models.TextField(
        help_text='Mailing address for CMR.', verbose_name='CMR Mailing Address', blank=True
    )
    address_nrhs = models.TextField(
        help_text='Mailing address for NRHS.', verbose_name='NRHS Mailing Address', blank=True
    )
    youtube = models.CharField(
        help_text='Youtube channel name without @ symbol. Example: cmr_railway.',
        verbose_name='Youtube',
        max_length=30,
        blank=True,
    )
    instagram = models.CharField(
        help_text='Instagram username without @ symbol. Example: cmr_railway.',
        verbose_name='Instagram',
        max_length=30,
        blank=True,
    )
    visit_addr = RichTextField(
        help_text='Visiting address for CMR layout and NRHS exhibits.',
        verbose_name='Visiting Address',
        blank=True,
    )
    visit_hours_MON = models.CharField(
        help_text='Visiting hours on Modays. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='MON',
        max_length=10,
        blank=True,
    )
    visit_hours_MON = models.CharField(
        help_text='Visiting hours on Monday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='MON',
        max_length=10,
        blank=True,
    )
    visit_hours_TUE = models.CharField(
        help_text='Visiting hours on Tuesday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='TUE',
        max_length=10,
        blank=True,
    )
    visit_hours_WED = models.CharField(
        help_text='Visiting hours on Wednesday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='WED',
        max_length=10,
        blank=True,
    )
    visit_hours_THU = models.CharField(
        help_text='Visiting hours on Thursday.Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='THU',
        max_length=10,
        blank=True,
    )
    visit_hours_FRI = models.CharField(
        help_text='Visiting hours on Friday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='FRI',
        max_length=10,
        blank=True,
    )
    visit_hours_SAT = models.CharField(
        help_text='Visiting hours on Saturday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='SAT',
        max_length=10,
        blank=True,
    )
    visit_hours_SUN = models.CharField(
        help_text='Visiting hours on Sunday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='SUN',
        max_length=10,
        blank=True,
    )
    visit_hours_holidays = models.CharField(
        help_text="Exceptions for holidays. Example: 'Holiday hours may differ.'",
        verbose_name='Holidays',
        max_length=30,
        blank=True,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('email_cmr'),
                FieldPanel('phone_cmr'),
                FieldPanel('address_cmr'),
                FieldPanel('email_nrhs'),
                FieldPanel('phone_nrhs'),
                FieldPanel('address_nrhs'),
                FieldPanel('youtube'),
                FieldPanel('instagram'),
                FieldPanel('visit_addr'),
            ],
            'Contact Settings',
        ),
        MultiFieldPanel(
            [
                FieldPanel('visit_hours_MON'),
                FieldPanel('visit_hours_TUE'),
                FieldPanel('visit_hours_WED'),
                FieldPanel('visit_hours_THU'),
                FieldPanel('visit_hours_FRI'),
                FieldPanel('visit_hours_SAT'),
                FieldPanel('visit_hours_SUN'),
                FieldPanel('visit_hours_holidays'),
            ],
            'Visiting Hours',
        ),
    ]


@register_snippet
class CopyrightText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    body = RichTextField()

    panels = [
        FieldPanel('body'),
        PublishingPanel(),
    ]

    def __str__(self):
        return 'Copyright text'

    def get_preview_template(self, request, mode_name):
        return 'base.html'

    def get_preview_context(self, request, mode_name):
        return {'copyright_text': self.body}

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = 'Copyright Text'


@register_snippet
class FooterText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    body = RichTextField()

    panels = [
        FieldPanel('body'),
        PublishingPanel(),
    ]

    def __str__(self):
        return 'Footer text'

    def get_preview_template(self, request, mode_name):
        return 'base.html'

    def get_preview_context(self, request, mode_name):
        return {'footer_text': self.body}

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = 'Footer Text'


@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'
