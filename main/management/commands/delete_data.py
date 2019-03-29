from django.core.management.base import BaseCommand
from openhumans.models import OpenHumansMember


class Command(BaseCommand):
    help = 'Delete data for user id'
    # meant to be used mostly for local development
    # and/or as the nuclear option if inconsistent state has been reached somehow

    def add_arguments(self, parser):
        parser.add_argument('--ohid')

    def handle(self, *args, **options):
        users = OpenHumansMember.objects.all()
        for user in users:
            if user.oh_id == options['ohid']:
                user.delete_all_files()
