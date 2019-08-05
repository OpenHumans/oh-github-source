from datetime import datetime
import json
import os
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