from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum, timezone
from django.utils.text import slugify

from factory import Faker

from wagtail.core.models import Page
from wagtail.rich_text import RichText

from base.models import CopyrightText, FooterText, Person, StandardPage
from blog.models import BlogMain, BlogPage
from home.models import HomePage


# from bakerydemo.breads.models import (
#     BreadIngredient,
#     BreadPage,
#     BreadsIndexPage,
#     BreadType,
#     Country,
# )
# from bakerydemo.locations.models import LocationPage, LocationsIndexPage

FIXTURE_MEDIA_DIR = Path(settings.PROJECT_DIR) / 'base/fixtures/media/original_images'


class Command(BaseCommand):
    help = 'Creates random data. Useful for performance or load testing.'

    def add_arguments(self, parser):
        parser.add_argument(
            'page_count',
            type=int,
            help='How many pages of each type to create',
        )
        parser.add_argument(
            'snippet_count',
            type=int,
            help='How many snippets of each type to create',
        )
        parser.add_argument(
            'image_count',
            type=int,
            help='How many images to create',
        )

    def fake_stream_field(self):
        return [('paragraph_block', RichText('\n'.join(lorem_ipsum.paragraphs(5))))]

    def get_random_model(self, model):
        return model.objects.order_by('?').first()

    def make_title(self):
        return lorem_ipsum.words(4, common=False)

    def create_home(self):
        self.stdout.write('Creating home page ...')

        # Only create new `HomePage` object if one
        # doesn't already exist
        homepage = HomePage.objects.live().first()
        if not homepage:
            root = Page.get_first_root_node()
            homepage = HomePage.objects.create(
                title='Home',
                slug='home',
                show_in_menus=True,
                show_promo=True,
                show_happening=True,
                show_newsletter=True,
                show_recent=True,
                max_recent=6,
                show_contact_info=True,
            )

            root.add_child(instance=homepage)

    def update_home(self):
        self.stdout.write('Updating home page ...')
        homepage = HomePage.objects.live().first()

        homepage.title = 'Home'
        homepage.slug = 'home'
        homepage.show_in_menus = True
        homepage.show_promo = True
        homepage.show_happening = True
        homepage.show_newsletter = True
        homepage.show_recent = True
        homepage.max_recent = 6
        homepage.show_contact_info = True
        homepage.promo_page = BlogPage.objects.live().first()

        homepage.save()

    def create_blog_main(self):
        self.stdout.write('Creating blog main page ...')
        home = HomePage.objects.live().first()

        blog_main = BlogMain.objects.create(
            title='Blog',
            slug='blog',
            show_in_menus=True,
            about=lorem_ipsum.paragraph(),
            about_title='About the blog',
            max_recent=6,
        )

        home.add_child(instance=blog_main)

    def create_pages(self, page_count):
        homepage = HomePage.objects.live().first()

        # self.stdout.write(f'Creating {page_count} bread page(s) ...')
        # breads_index = BreadsIndexPage.objects.live().first()
        # for _ in range(page_count):
        #     title = self.make_title()
        #     breads_index.add_child(
        #         instance=BreadPage(
        #             title=title,
        #             slug=slugify(title),
        #             introduction=lorem_ipsum.paragraph(),
        #             bread_type=self.get_random_model(BreadType),
        #             body=self.fake_stream_field(),
        #             origin=self.get_random_model(Country),
        #             image=self.get_random_model(Image),
        #         )
        #     )

        # self.stdout.write(f'Creating {page_count} location page(s) ...')
        # locations_index = LocationsIndexPage.objects.live().first()
        # for _ in range(page_count):
        #     title = self.make_title()
        #     locations_index.add_child(
        #         instance=LocationPage(
        #             title=title,
        #             slug=slugify(title),
        #             introduction=lorem_ipsum.paragraph(),
        #             image=self.get_random_model(Image),
        #             address=lorem_ipsum.paragraph(),
        #             body=self.fake_stream_field(),
        #             lat_long="64.144367, -21.939182",
        #         )
        #     )

        self.stdout.write(f'Creating {page_count} blog page(s) ...')
        blog_main = BlogMain.objects.live().first()
        for _ in range(page_count):
            title = self.make_title()
            blog_main.add_child(
                instance=BlogPage(
                    date=timezone.now(),
                    title=title,
                    slug=slugify(title),
                    subtitle=lorem_ipsum.words(10, common=False),
                    intro=lorem_ipsum.paragraph(),
                    body=self.fake_stream_field(),
                )
            )

        self.stdout.write('Creating T&C and Privacy pages ...')
        homepage.add_child(
            instance=StandardPage(
                title='Terms and Conditions',
                slug=slugify(title),
                intro=lorem_ipsum.paragraph(),
                body=self.fake_stream_field(),
            )
        )
        homepage.add_child(
            instance=StandardPage(
                title='Privacy Policy',
                slug=slugify(title),
                intro=lorem_ipsum.paragraph(),
                body=self.fake_stream_field(),
            )
        )

    def create_snippets(self, snippet_count):
        self.stdout.write(f'Creating {snippet_count} people ...')
        for _ in range(snippet_count):
            Person.objects.create(
                first_name=Faker('first_name'),
                last_name=Faker('last_name'),
                street=Faker('street_address'),
                city=Faker('city'),
                state=Faker('state'),
                zip=Faker('postcode'),
                email=Faker('ascii_safe_email'),
                # image=self.get_random_model(Image),
            )

        self.stdout.write('Creating footer text ...')
        FooterText.objects.create(body=self.fake_stream_field())

        self.stdout.write('Creating copyright text ...')
        CopyrightText.objects.create(body=self.fake_stream_field())

    def create_images(self, image_count):
        # image_files = list(FIXTURE_MEDIA_DIR.iterdir())

        self.stdout.write(f'Creating {image_count} image(s) ...')
        # for _ in range(image_count):
        #     random_image = random.choice(image_files)
        #     with random_image.open(mode="rb") as image_file:
        #         willow_image = WillowImage.open(image_file)
        #         width, height = willow_image.get_size()
        #         image = Image.objects.create(
        #             title=self.make_title(),
        #             width=width,
        #             height=height,
        #             file_size=random_image.stat().st_size,
        #         )
        #         image_file.seek(0)
        #         image.file.save(random_image.name, image_file)

    def handle(self, **options):
        self.create_images(options['image_count'])
        self.create_snippets(options['snippet_count'])
        self.create_home()
        self.create_blog_main()
        self.create_pages(options['page_count'])
        self.update_home()

        self.stdout.write('Done!')
