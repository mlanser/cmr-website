from django.db import models

from modelcluster.fields import ParentalKey
from phonenumber_field.modelfields import PhoneNumberField

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    PublishingPanel,
)

from wagtail.fields import RichTextField, StreamField
from wagtail.models import (
    Page,
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
)

from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel

from wagtail.contrib.settings.models import BaseGenericSetting, register_setting

from wagtail.snippets.models import register_snippet
from wagtail.search import index

from sections.blocks import SectionPageStreamBlock


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
    visit_addr = models.TextField(
        help_text='Visiting address for CMR layout and NRHS exhibits.',
        verbose_name='Visiting Address',
        blank=True,
    )
    open_MON = models.CharField(
        default='',
        help_text='Visiting hours on Modays. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='MON',
        max_length=10,
        blank=True,
    )
    open_TUE = models.CharField(
        default='',
        help_text='Visiting hours on Tuesday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='TUE',
        max_length=10,
        blank=True,
    )
    open_WED = models.CharField(
        default='',
        help_text='Visiting hours on Wednesday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='WED',
        max_length=10,
        blank=True,
    )
    open_THU = models.CharField(
        default='7P - 9P',
        help_text='Visiting hours on Thursday.Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='THU',
        max_length=10,
        blank=True,
    )
    open_FRI = models.CharField(
        default='',
        help_text='Visiting hours on Friday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='FRI',
        max_length=10,
        blank=True,
    )
    open_SAT = models.CharField(
        default='10A - 5P',
        help_text='Visiting hours on Saturday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='SAT',
        max_length=10,
        blank=True,
    )
    open_SUN = models.CharField(
        default='2P - 5P',
        help_text='Visiting hours on Sunday. Leave blank if not open to public. Example: 10A - 5P.',
        verbose_name='SUN',
        max_length=10,
        blank=True,
    )
    open_holidays = models.CharField(
        default='Holiday hours may differ.',
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
                FieldPanel('open_MON'),
                FieldPanel('open_TUE'),
                FieldPanel('open_WED'),
                FieldPanel('open_THU'),
                FieldPanel('open_FRI'),
                FieldPanel('open_SAT'),
                FieldPanel('open_SUN'),
                FieldPanel('open_holidays'),
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
    body = models.TextField(
        help_text='Copyright text to display in the footer.',
    )

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


class ContactField(AbstractFormField):
    page = ParentalKey('ContactForm', on_delete=models.CASCADE, related_name='contact_fields')


class ContactForm(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro'),
        InlinePanel('contact_fields', label='Contact Form fields'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('from_address'),
                        FieldPanel('to_address'),
                    ]
                ),
                FieldPanel('subject'),
            ],
            'Email',
        ),
    ]


# Plain standard page without banner or header sections
#
# NOTE: This is a simple page with a basic fields (e.g. title,
#       body, etc.) and it's best used for pages sugas T&C, etc.
class StandardPage(Page):
    # Database fields
    intro = models.CharField(max_length=250)
    body = StreamField(
        SectionPageStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text='Create a plain page without sidebar using Markdown.',
    )

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['home.HomePage']
    subpage_types = []

    # Misc fields, helpers, and custom methods
    page_description = 'Use this content type for pages without sidebar (e.g. legal, T&C, etc.).'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['DEBUG'] = 'DEBUG'  # Placeholder for custom context variables
        return context


# Abstract model for banner slide
class BannerSlide(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Slide image',
        help_text='Image for the slide',
    )
    text = models.CharField(
        blank=True,
        max_length=255,
        verbose_name='Slide text',
        help_text='Text to display on the slide',
    )
    url = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Slide link',
        help_text='Optional link for the slide',
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('text'),
        FieldPanel('url'),
    ]

    class Meta:
        abstract = True


# Abstract model for event tile
class EventItem(models.Model):
    event_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promoted event',
        help_text='Select event content to promote on home page',
    )

    panels = [
        PageChooserPanel('event_page', 'sections.SectionPage'),
    ]

    class Meta:
        abstract = True
