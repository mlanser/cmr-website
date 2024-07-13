from django.db import models


from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page


class HomePage(Page):
    # Database fields
    # --------------------------------
    # Banner Section -- Max 4 slides
    slide01 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image for slide #1',
    )
    slide01_text = models.CharField(
        blank=True,
        verbose_name='Text for slide #1',
        max_length=255,
        help_text='Text to display on slide #1',
    )
    slide01_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='CTA link for slide #1',
        help_text='Optional link for slide #1',
    )

    slide02 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image for slide #2',
    )
    slide02_text = models.CharField(
        blank=True,
        verbose_name='Text for slide #2',
        max_length=255,
        help_text='Text to display on slide #2',
    )
    slide02_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='CTA link for slide #2',
        help_text='Optional link for slide #2',
    )

    slide03 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image for slide #3',
    )
    slide03_text = models.CharField(
        blank=True,
        verbose_name='Text for slide #3',
        max_length=255,
        help_text='Text to display on slide #3',
    )
    slide03_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='CTA link for slide #3',
        help_text='Optional link for slide #3',
    )

    slide04 = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image for slide #4',
    )
    slide04_text = models.CharField(
        blank=True,
        verbose_name='Text for slide #4',
        max_length=255,
        help_text='Text to display on slide #4',
    )
    slide04_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='CTA link for slide #4',
        help_text='Optional link for slide #4',
    )

    # Editor panels configuration
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('slide01'),
                FieldPanel('slide01_text'),
                FieldPanel('slide01_link'),
            ],
            heading='Banner Slide #1',
        ),
        MultiFieldPanel(
            [
                FieldPanel('slide02'),
                FieldPanel('slide02_text'),
                FieldPanel('slide02_link'),
            ],
            heading='Banner Slide #2',
        ),
        MultiFieldPanel(
            [
                FieldPanel('slide03'),
                FieldPanel('slide03_text'),
                FieldPanel('slide03_link'),
            ],
            heading='Banner Slide #3',
        ),
        MultiFieldPanel(
            [
                FieldPanel('slide04'),
                FieldPanel('slide04_text'),
                FieldPanel('slide04_link'),
            ],
            heading='Banner Slide #4',
        ),
        # FieldPanel('body'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, 'Common page configuration'),
    ]

    # Search index configuration
    # search_fields = Page.search_fields + [
    #     index.SearchField('body'),
    # ]

    # Parent page / subpage type rules
    # subpage_types = ['section_main.SectionMainPage']

    # Misc fields, helpers, and custom methods
    page_description = 'Use this content type for the home page.'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return updated context
        context['showBanner'] = True
        context['showMeta'] = False
        context['showContact'] = True
        context['DEBUG'] = 'DEBUG'  # Placeholder for custom context variables

        context['slides'] = []
        if self.slide01:
            context['slides'].append(
                {'image': self.slide01, 'text': self.slide01_text, 'link': self.slide01_link}
            )
        if self.slide02:
            context['slides'].append(
                {'image': self.slide02, 'text': self.slide02_text, 'link': self.slide02_link}
            )
        if self.slide03:
            context['slides'].append(
                {'image': self.slide03, 'text': self.slide03_text, 'link': self.slide03_link}
            )
        if self.slide04:
            context['slides'].append(
                {'image': self.slide04, 'text': self.slide04_text, 'link': self.slide04_link}
            )

        # sectionpages = self.get_children().live().order_by('-first_published_at')
        # context['sectionpages'] = sectionpages
        return context

    # def main_image(self):
    #     return self.feed_image or None

    # ////////////////////////////////////////
    # feed_image = models.ForeignKey(
    #     'wagtailimages.Image',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='+'
    # )
    # body = RichTextField(blank=True)
    # body = StreamField(
    #     SectionMainStreamBlock(),
    #     blank=True,
    #     use_json_field=True,
    #     help_text='Create a landing/main page for a section using Markdown.',
    # )

    # # modify your content_panels:
    # content_panels = Page.content_panels + [
    #     MultiFieldPanel(
    #         [
    #             FieldPanel("image"),
    #             FieldPanel("hero_text"),
    #             FieldPanel("hero_cta"),
    #             FieldPanel("hero_cta_link"),
    #         ],
    #         heading="Hero section",
    #     ),
    #     FieldPanel('body'),
    # ]
