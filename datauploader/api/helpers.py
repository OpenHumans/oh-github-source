from datetime import datetime
import json
import os
import requests
import tempfile


def write_jsonfile_to_tmp_dir(filename, json_data):
    tmp_dir = tempfile.mkdtemp()
    full_path = os.path.join(tmp_dir, filename)
    with open(full_path, 'w') as json_file:
        json_file.write(json.dumps(json_data))
        json_file.flush()
    return full_path

def create_file_metadata():
    return {
        'description':
            'Github data.',
        'tags': ['Github', 'github', 'commits', 'code', 'repos'],
        'updated_at': str(datetime.utcnow()),
    }

def get_existing_file_ids(oh_member):
    # Right now this should be maximum one existing file
    ids = []
    for file_info in oh_member.list_files():
        if 'Github' in file_info['metadata']['tags']:
            id = file_info['id']
            ids.append(id)
    return ids


def download_to_json(download_url):
    return json.loads(requests.get(download_url).content)


def get_commit_date(commit_rest_obj):
    return commit_rest_obj['commit']['committer']['date']