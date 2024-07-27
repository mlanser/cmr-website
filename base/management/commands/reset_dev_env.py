from django.conf import settings
from django.core.cache import caches
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from django_extensions.settings import POSTGRESQL_ENGINES

from wagtail.documents import get_document_model
from wagtail.images import get_image_model


class Command(BaseCommand):
    def handle(self, **options):
        # if settings.DATABASES[DEFAULT_DB_ALIAS]["ENGINE"] in POSTGRESQL_ENGINES:
        #     raise CommandError(
        #         "This command can be used only with PostgreSQL databases."
        #     )

        # 1. (optional) Remove all objects from S3
        if "s3" in settings.DEFAULT_FILE_STORAGE:
            self.stdout.write("Removing files from S3")
            # default_storage.bucket.objects.all().delete()
        else:
            self.stdout.write("Removing images")
            # get_image_model().objects.all().delete()

            self.stdout.write("Removing documents")
            # get_document_model().objects.all().delete()

        # 2. Reset database to nothing
        self.stdout.write('Resetting database ...')
        # call_command("reset_schema", interactive=False)
        call_command('reset_db', '--noinput')
        self.stdout.write('Resetting database ... done!')

        # 3. Rebuild database
        self.stdout.write('Running migrations ...')
        call_command('migrate', interactive=False)
        self.stdout.write('Running migrations ... done!')

        # 4. Clear caches
        self.stdout.write('Clearing cache ...')
        for cache in caches.all():
            cache.clear()
        self.stdout.write('Clearing cache ... done!')

        # 5. Re-import data
        self.stdout.write('Loading initial data ...')
        # call_command("load_initial_data")
        self.stdout.write('Loading initial data ... done!')

        # 6. Change the admin password (in case it's different in this environment)
        self.stdout.write('Resetting admin password ...')
        call_command('reset_admin_password')
        self.stdout.write('Resetting admin password ... done!')
