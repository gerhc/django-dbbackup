import os
import subprocess
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from django.conf import settings
from dbbackup.storage.base import BaseStorage

BASE_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt')
ENCRYPTED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gpg')
COMPRESSED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gz')
ENCRYPTED_COMPRESSED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gz.gpg')
TEST_DATABASE = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/foo.db', 'USER': 'foo', 'PASSWORD': 'bar', 'HOST': 'foo', 'PORT': 122}

GPG_PRIVATE_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/secring.gpg')
GPG_PUBLIC_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/pubring.gpg')
GPG_FINGERPRINT = '7438 8D4E 02AF C011 4E2F  1E79 F7D1 BBF0 1F63 FDE9'
DEV_NULL = open(os.devnull, 'w')


class handled_files(dict):
    """Dict for gather information about fake storage and clean between tests."""
    def __init__(self):
        super(handled_files, self).__init__()
        self.clean()

    def clean(self):
        self['written_files'] = []
        self['deleted_files'] = []
HANDLED_FILES = handled_files()


class FakeStorage(BaseStorage):
    name = 'FakeStorage'
    list_files = ['foo', 'bar']
    deleted_files = []
    file_read = ENCRYPTED_FILE

    def delete_file(self, filepath):
        HANDLED_FILES['deleted_files'].append(filepath)
        self.deleted_files.append(filepath)

    def list_directory(self, raw=False):
        return self.list_files

    def write_file(self, filehandle, filename):
        HANDLED_FILES['written_files'].append((filename, filehandle))

    def read_file(self, filepath):
        return open(self.file_read, 'rb')

Storage = FakeStorage


def clean_gpg_keys():
        try:
            cmd = ("gpg --batch --yes --delete-key '%s'" % GPG_FINGERPRINT)
            subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
        except:
            pass
        try:
            cmd = ("gpg --batch --yes --delete-secrect-key '%s'" % GPG_FINGERPRINT)
            subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
        except:
            pass
