from wagtail.blocks import CharBlock, ChoiceBlock, RichTextBlock, StreamBlock, StructBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.blocks import MarkdownBlock


class ImageBlock(StructBlock):
    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = 'image'
        template = 'base/blocks/image_block.html'


class HeadingBlock(StructBlock):
    heading_text = CharBlock(classname='title', required=True)
    size = ChoiceBlock(
        choices=[
            ('', 'Select heading size'),
            ('h2', 'H2'),
            ('h3', 'H3'),
            ('h4', 'H4'),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = 'title'
        template = 'base/blocks/heading_block.html'


class BaseStreamBlock(StreamBlock):
    heading_block = HeadingBlock()
    richtext_block = RichTextBlock(icon='pilcrow')
    markdown_block = MarkdownBlock(icon='code')
    image_block = ImageBlock()
    embed_block = EmbedBlock(
        help_text='Insert a URL to embed. For example, https://www.youtube.com/watch?v=SGJFWirQ3ks',
        icon='media',
    )
