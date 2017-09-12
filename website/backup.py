import gzip
import os
import shutil

from django.core import management


def create_json_dump(filepath):
    filepath_compressed = filepath + '.gz'
    with open(filepath, 'w') as fileout:
        management.call_command(
            'dumpdata',
            '--all',
            '--natural-foreign',
            'website',
            'observation',
            stdout=fileout
        )
    with open(filepath, 'rb') as f_in:
        with gzip.open(filepath_compressed, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(filepath)
