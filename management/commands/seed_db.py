from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from example.models import Author, Book


class Command(BaseCommand):
    help = 'Seed database with sample data.'

    @transaction.atomic
    def handle(self, *args, **options):
        if Author.objects.exists():
            raise CommandError(
                'This command cannot be run when any authors exist to guard against accidental use on production.'
            )

        self.stdout.write('Seeding database...')

        update_site()
        create_authors_and_books()

        self.stdout.write('Done.')


def update_site():
    domain = settings.LOCAL_DEV_DOMAIN
    Site.objects.filter(domain=settings.PROD_DOMAIN).update(domain=domain, name=domain)


def create_authors_and_books():
    def make_books(author, titles):
        Book.objects.bulk_create([Book(author=author, title=title) for title in titles])

    marcus = Author.objects.create(
        name='Marcus Aurelius',
    )
    make_books(
        marcus,
        [
            'Meditations',
        ],
    )

    jane = Author.objects.create(name='Jane Austen')
    make_books(
        jane,
        [
            'Sense and Sensibility',
            'Pride and Prejudice',
            'Mansfield Park',
            'Emma',
            'Northanger Abbey',
            'Persuasion',
            'Lady Susan',
        ],
    )
