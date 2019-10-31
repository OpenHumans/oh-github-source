from django.core.management.base import BaseCommand
from main.models import DataSourceMember
from datauploader.tasks import process_github
import arrow
from datetime import timedelta


class Command(BaseCommand):
    help = 'Updates data for all members'

    def handle(self, *args, **options):
        users = DataSourceMember.objects.all()
        for github_user in users:
            if github_user.last_updated < (arrow.now() - timedelta(days=1)):
                print("Updating user {}".format(github_user.user.oh_id))
                oh_id = github_user.user.oh_id
                process_github.delay(oh_id)
            else:
                print("Did not update {}".format(github_user.user.oh_id))
