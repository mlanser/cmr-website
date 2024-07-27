from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError('This command is only available in DEBUG mode.')

        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist as e:
            raise CommandError('Cannot find admin user.') from e

        admin_user.set_password(settings.ADMIN_PASSWORD)
        admin_user.save(update_fields=['password'])
