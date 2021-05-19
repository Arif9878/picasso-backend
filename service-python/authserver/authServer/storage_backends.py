import os, uuid
from storages.backends.s3boto3 import S3Boto3Storage

def path_and_rename(prefix, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(prefix, filename)

def get_path_file(instance, filename):
    return path_and_rename('', filename)

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = True

class ProfileMediaStorage(S3Boto3Storage):
    location = 'media/profile'
    file_overwrite = True