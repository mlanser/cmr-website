from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.blocks import MarkdownBlock


class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for displaying images with associated caption,
    ALT text, and attribution data.
    """

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    credit_text = CharBlock(required=False)
    credit_url = URLBlock(required=False)

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


class BlockQuote(StructBlock):
    """
    Custom `StructBlock` for quotes with attribute to the author
    """

    text = TextBlock()
    attribute_name = CharBlock(
        blank=True, 
        required=False, 
        label="e.g. Mary Berry"
    )

    class Meta:
        icon = "openquote"
        template = "blocks/blockquote.html"


class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks for the `StreamField`
    """

    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(
        icon="pilcrow", 
        template="blocks/paragraph_block.html"
    )
    # markdown_block = MarkdownBlock(icon='code')
    image_block = ImageBlock()
    embed_block = EmbedBlock(
        help_text='Insert a URL to embed. For example, https://www.youtube.com/watch?v=SGJFWirQ3ks',
        icon='media',
        template="blocks/embed_block.html"
    )
