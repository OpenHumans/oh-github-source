"""
Asynchronous tasks that update data in Open Humans.
These tasks:
  1. delete any current files in OH if they match the planned upload filename
  2. adds a data file
"""
import logging
import json
import tempfile
import requests
import os
from celery import shared_task
from django.conf import settings
from openhumans.models import OpenHumansMember
from datetime import datetime, timedelta
from datauploader.api.gql import TEST_QUERY, graphql_query
from demotemplate.settings import rr
from requests_respectful import RequestsRespectfulRateLimitedError
from ohapi import api
import arrow

import datauploader.api.rest as gh_api
from datauploader.api.helpers import create_file_metadata

# Set up logging.
logger = logging.getLogger(__name__)

MAX_FILE_BYTES = 256000000


@shared_task
def process_github(oh_id):
    """
    Update the github file for a given OH user
    """
    logger.debug('Starting github processing for {}'.format(oh_id))
    oh_member = OpenHumansMember.objects.get(oh_id=oh_id)
    oh_access_token = oh_member.get_access_token(
                            client_id=settings.OPENHUMANS_CLIENT_ID,
                            client_secret=settings.OPENHUMANS_CLIENT_SECRET)
    #github_data = get_existing_github_data(oh_access_token)#
    github_member = oh_member.datasourcemember
    github_access_token = github_member.get_access_token(
                            client_id=settings.GITHUB_CLIENT_ID,
                            client_secret=settings.GITHUB_CLIENT_SECRET)

    current_dt = datetime.utcnow()

    gh_file = gh_api.get_github_data(oh_member, github_access_token, current_dt)

    api.upload_aws(gh_file, create_file_metadata(),
                   oh_access_token,
                   project_member_id=oh_id,
                   max_bytes=MAX_FILE_BYTES)

    github_member.last_updated = arrow.now().format()
    github_member.save()



def get_existing_github_data(oh_access_token):
    member = api.exchange_oauth2_member(oh_access_token)
    for dfile in member['data']:
        if 'Github' in dfile['metadata']['tags']:
            # get file here and read the json into memory
            tf_in = tempfile.NamedTemporaryFile(suffix='.json')
            tf_in.write(requests.get(dfile['download_url']).content)
            tf_in.flush()
            github_data = json.load(open(tf_in.name))
            return github_data
    return []
