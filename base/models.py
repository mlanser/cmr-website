from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from phonenumber_field.modelfields import PhoneNumberField

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    PublishingPanel,
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel

from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import (
    Collection,
    DraftStateMixin,
    LockableMixin,
    Page,
    PreviewableMixin,
    RevisionMixin,
    Task,
    TaskState,
    TranslatableMixin,
    WorkflowMixin,
)
from wagtail.search import index

from base.blocks import BaseStreamBlock


# ---------------------------------------------------------
#         C O R E   H E L P E R   C L A S S E S
# ---------------------------------------------------------
@register_setting(icon='site')
class ContactSettings(ClusterableModel, BaseGenericSetting):
    email_cmr = models.EmailField(
        help_text='Email address for CMR', verbose_name='CMR email', blank=True
    )
    email_nrhs = models.EmailField(
        help_text='Email address for NRHS', verbose_name='NRHS email', blank=True
    )
    phone_cmr = PhoneNumberField(
        help_text='Phone number for CMR', verbose_name='CMR phone', blank=True
    )
    phone_nrhs = PhoneNumberField(
        help_text='Phone number for NRHS', verbose_name='NRHS phone', blank=True
    )
    address_cmr = models.TextField(
        help_text='Mailing address for CMR.', verbose_name='CMR mailing address', blank=True
    )
    address_nrhs = models.TextField(
        help_text='Mailing address for NRHS.', verbose_name='NRHS mailing address', blank=True
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
    github = models.CharField(
        help_text='Github username without @ symbol. Example: cmr_railway.',
        verbose_name='Github',
        max_length=30,
        blank=True,
    )

    visit_addr = models.TextField(
        help_text='Visiting address for CMR layout and NRHS exhibits.',
        verbose_name='Visiting address',
        blank=True,
    )
    visit_map_link = models.URLField(
        help_text='Map link for visiting address.',
        verbose_name='Map link',
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
                FieldPanel('github'),
                FieldPanel('visit_addr'),
                FieldPanel('visit_map_link'),
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


@register_setting(icon='site')
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name='Title suffix',
        max_length=255,
        help_text="The suffix for the title meta tag e.g. ' | Carolina Model Railroaders'",
        default='Carolina Model Railroaders',
    )

    terms_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='T&Cs page',
        help_text='Select T&Cs page for links in footer.',
    )
    privacy_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Privacy page',
        help_text='Select privacy page for links in footer.',
    )
    rss_link = models.URLField(
        help_text='Link for RSS feed.',
        verbose_name='RSS link',
        blank=True,
    )

    panels = [
        FieldPanel('title_suffix'),
        PageChooserPanel('terms_page', 'base.StandardPage'),
        PageChooserPanel('privacy_page', 'base.StandardPage'),
        FieldPanel('rss_link'),
    ]


class CopyrightText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    """
    Editable text for the copyright text in the website footer.

    It is registered using `register_snippet` as a function in `wagtail_hooks.py`
    to be grouped with the `Person` model inside the same main menu item. It is made
    accessible on the template via a template tag defined in base/templatetags/
    navigation_tags.py

    TODO:
    [ ] Add `faker` factory in `factories.py`
    [ ] Add seeding function for DEV environment
    """

    body = models.TextField(
        help_text='Copyright text to display in the footer.',
    )

    revisions = GenericRelation(
        'wagtailcore.Revision',
        content_type_field='base_content_type',
        object_id_field='object_id',
        related_query_name='copyright_text',
        for_concrete_model=False,
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
        verbose_name = 'Copyright text'
        verbose_name_plural = 'Copyright text'


class FooterText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    """
    Editable additional (non-copyright) text in the website footer.

    It is registered using `register_snippet` as a function in `wagtail_hooks.py` to
    be grouped with the `Person` model inside the same main menu item. It is made
    accessible on the template via a template tag defined in base/templatetags/
    navigation_tags.py

    TODO:
    [ ] Add `faker` factory in `factories.py`
    [ ] Add seeding function for DEV environment
    """

    body = RichTextField()

    revisions = GenericRelation(
        'wagtailcore.Revision',
        content_type_field='base_content_type',
        object_id_field='object_id',
        related_query_name='footer_text',
        for_concrete_model=False,
    )

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
        verbose_name = 'Footer text'
        verbose_name_plural = 'Footer text'


class Person(
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    PreviewableMixin,
    index.Indexed,
    ClusterableModel,
):
    """
    Person object - using standard Django model

    It is registered using `register_snippet` as a function in wagtail_hooks.py
    to allow it to have a menu item within a custom menu item group.

    `Person` uses the `ClusterableModel`, which allows the relationship with
    another model to be stored locally to the 'parent' model (e.g. a PageModel)
    until the parent is explicitly saved. This allows the editor to use the
    'Preview' button, to preview the content, without saving the relationships
    to the database.

    https://github.com/wagtail/django-modelcluster

    TODO:
    [x] Add `faker` factory in `factories.py`
    [ ] Change `get_preview_template` to not use `BlogPage`
    [ ] Change `get_preview_context` to not use `BlogPage`
    """

    first_name = models.CharField('First name', max_length=255)
    last_name = models.CharField('Last name', max_length=255)
    email = models.EmailField('Email', blank=True)
    street = models.CharField('First name', blank=True, max_length=255)
    city = models.CharField('First name', blank=True, max_length=255)
    state = models.CharField('First name', blank=True, max_length=255)
    zip = models.CharField('First name', blank=True, max_length=255)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    workflow_states = GenericRelation(
        'wagtailcore.WorkflowState',
        content_type_field='base_content_type',
        object_id_field='object_id',
        related_query_name='person',
        for_concrete_model=False,
    )

    revisions = GenericRelation(
        'wagtailcore.Revision',
        content_type_field='base_content_type',
        object_id_field='object_id',
        related_query_name='person',
        for_concrete_model=False,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('first_name'),
                        FieldPanel('last_name'),
                    ]
                )
            ],
            'Name',
        ),
        FieldPanel('email'),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('street'),
                        FieldPanel('city'),
                        FieldPanel('state'),
                        FieldPanel('zip'),
                    ]
                )
            ],
            'Mailing address',
        ),
        FieldPanel('image'),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField('first_name'),
        index.SearchField('last_name'),
        index.SearchField('city'),
        index.SearchField('state'),
        index.SearchField('zip'),
        index.AutocompleteField('first_name'),
        index.AutocompleteField('last_name'),
    ]

    @property
    def thumb_image(self):
        # Returns an empty string if there is no profile pic or the rendition
        # file can't be found.
        try:
            return self.image.get_rendition('fill-50x50').img_tag()
        except Exception:
            return ''

    @property
    def preview_modes(self):
        return PreviewableMixin.DEFAULT_PREVIEW_MODES + [('blog_post', _('Blog post'))]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_preview_template(self, request, mode_name):
        from blog.models import BlogPage

        if mode_name == 'blog_post':
            return BlogPage.template
        return 'base/preview/person.html'

    def get_preview_context(self, request, mode_name):
        from blog.models import BlogPage

        context = super().get_preview_context(request, mode_name)
        if mode_name == self.default_preview_mode:
            return context

        page = BlogPage.objects.filter(blog_person_relationship__person=self).first()
        if page:
            # Use the page authored by this person if available,
            # and replace the instance from the database with the edited instance
            page.authors = [self if author.pk == self.pk else author for author in page.authors()]
            # The authors() method only shows live authors, so make sure the instance
            # is included even if it's not live as this is just a preview
            if not self.live:
                page.authors.append(self)
        else:
            # Otherwise, get the first page and simulate the person as the author
            page = BlogPage.objects.first()
            page.authors = [self]

        context['page'] = page
        return context

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'


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


class FormField(AbstractFormField):
    """
    Wagtailforms is a module to introduce simple forms on a Wagtail site. It
    isn't intended as a replacement to Django's form support but as a quick way
    to generate a general purpose data-collection form or contact form
    without having to write code. We use it on the site for a contact form. You
    can read more about Wagtail forms at:
    https://docs.wagtail.org/en/stable/reference/contrib/forms/index.html
    """

    page = ParentalKey('FormPage', related_name='form_fields', on_delete=models.CASCADE)


class FormPage(AbstractEmailForm):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    body = StreamField(BaseStreamBlock(), use_json_field=True)
    thank_you_text = RichTextField(blank=True)

    # Note how we include the FormField object via an InlinePanel using the
    # related_name value
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('image'),
        FieldPanel('body'),
        InlinePanel('form_fields', heading='Form fields', label='Field'),
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


# Advert model
class Advert(PreviewableMixin, index.Indexed, models.Model):
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255)
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')

    panels = [
        FieldPanel('url'),
        FieldPanel('text'),
        FieldPanel('image'),
    ]

    search_fields = [
        index.SearchField('text'),
        index.AutocompleteField('text'),
    ]

    def __str__(self):
        return self.text

    @property
    def preview_modes(self):
        return PreviewableMixin.DEFAULT_PREVIEW_MODES + [('alt', 'Alternate')]

    def get_preview_template(self, request, mode_name):
        templates = {
            '': 'base/previews/advert.html',  # Default preview mode
            'alt': 'base/previews/advert_alt.html',  # Alternate preview mode
        }
        return templates.get(mode_name, templates[''])

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        if mode_name == 'alt':
            context['extra_context'] = 'Alternate preview mode'
        return context


class RelatedLink(models.Model):
    """
    Abstract model for related links.

    This model is used to create links between related content pages.
    """

    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
    ]

    class Meta:
        abstract = True


class GalleryImage(models.Model):
    """
    Abstract model for gallery images.

    This model is used to create links to one or more images
    and it includes fields for captions and credits.

    TODO:
    [ ] Add `faker` factory in `factories.py`
    """

    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Gallery image',
        help_text='Use image ratio 3:2 and max size 1200 x 800 px.',
    )
    caption = models.CharField(
        blank=True,
        max_length=255,
        verbose_name='Image caption',
        help_text='Text is used as ALT text for the image.',
    )
    credit_text = models.CharField(
        blank=True,
        max_length=255,
        verbose_name='Image credit',
        help_text='Image credits display below image.',
    )
    credit_url = models.URLField(
        blank=True, verbose_name='Credit URL', help_text='URL for image credits.'
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),  # ALT text
        FieldPanel('credit_text'),
        FieldPanel('credit_url'),
    ]

    class Meta:
        abstract = True


class BannerImage(models.Model):
    """
    Abstract model for banner images.

    This model is used to create links to one or more banner images
    and it includes fierlds for captions and credit.

    TODO:
    [ ] Add `faker` factory in `factories.py`
    """

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner image',
        help_text='Use image ratio 20:9 and max size 2000 x 900 px',
    )
    caption = models.CharField(
        blank=True,
        max_length=255,
        verbose_name='Banner text',
        help_text='Optional text to display on the banner image',
    )
    credit_text = models.CharField(
        blank=True,
        max_length=255,
        verbose_name='Image credit',
        help_text='Image credits display below image.',
    )
    credit_url = models.URLField(
        blank=True, verbose_name='Credit URL', help_text='URL for image credits.'
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),  # ALT text
        FieldPanel('credit_text'),
        FieldPanel('credit_url'),
    ]

    class Meta:
        abstract = True


class GalleryPage(Page):
    """
    Gallery page to display a list of images.

    Use a Q object to list any Collection created (/admin/collections/) even if they
    contain no items.
    """

    introduction = models.TextField(help_text='Text to describe the page', blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and ' '3000px.',
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name='Page body', blank=True, use_json_field=True
    )
    collection = models.ForeignKey(
        Collection,
        limit_choices_to=~models.Q(name__in=['Root']),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Select the image collection for this gallery.',
    )

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
        FieldPanel('image'),
        FieldPanel('collection'),
    ]

    # Defining what content type can sit under the parent. Since it's a blank
    # array no subpage can be added
    subpage_types = []


class UserApprovalTaskState(TaskState):
    pass


class UserApprovalTask(Task):
    """
    Based on https://docs.wagtail.org/en/stable/extending/custom_tasks.html.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False
    )

    admin_form_fields = Task.admin_form_fields + ['user']

    task_state_class = UserApprovalTaskState

    # prevent editing of `user` after the task is created
    # by default, this attribute contains the 'name' field to prevent tasks from being renamed
    admin_form_readonly_on_edit_fields = Task.admin_form_readonly_on_edit_fields + ['user']

    def user_can_access_editor(self, page, user):
        return user == self.user

    def page_locked_for_user(self, page, user):
        return user != self.user

    def get_actions(self, page, user):
        if user == self.user:
            return [
                ('approve', 'Approve', False),
                ('reject', 'Reject', False),
                ('cancel', 'Cancel', False),
            ]
        else:
            return []

    def on_action(self, task_state, user, action_name, **kwargs):
        if action_name == 'cancel':
            return task_state.workflow_state.cancel(user=user)
        else:
            return super().on_action(task_state, user, action_name, **kwargs)

    def get_task_states_user_can_moderate(self, user, **kwargs):
        if user == self.user:
            # get all task states linked to the (base class of) current task
            return TaskState.objects.filter(
                status=TaskState.STATUS_IN_PROGRESS, task=self.task_ptr
            )
        else:
            return TaskState.objects.none()

    @classmethod
    def get_description(cls):
        return _('Only a specific user can approve this task')


# ---------------------------------------------------------
#           C O R E   P A G E   M O D E L S
# ---------------------------------------------------------
class StandardPage(Page):
    """
    Standard Page - RichText Format

    Plain standard page without banner or header sections

    This is a simple page with a basic fields (e.g. title, body, etc.)
    and it's best used for pages such as T&C, etc.

    TODO:
    [ ] Add `faker` factory in `factories.py`
    """

    # --------------------------------
    # Database fields
    # --------------------------------
    intro = models.CharField(max_length=255)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.',
    )
    body = RichTextField(
        blank=True,
        help_text='Create a plain page without sidebar using RichText format.',
    )

    # --------------------------------
    # Editor panels & search index configuration
    # --------------------------------
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('image'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
    ]

    # --------------------------------
    # Parent page / subpage type rules
    # --------------------------------
    parent_page_types = ['home.HomePage']
    subpage_types = []

    # --------------------------------
    # Misc fields, helpers, and custom methods
    # --------------------------------
    page_description = 'Use this content type for pages without sidebar (e.g. legal, T&C, etc.).'
    template = 'base/standard_page.html'

    def __str__(self):
        return f'Standard page - {self.title}'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['show_meta'] = True
        context['show_intro'] = False
        context['is_richtext'] = True
        return context
