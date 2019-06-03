import uuid

import botocore
from boto3 import resource, Session
from flask import current_app
from notifications_utils.s3 import s3upload as utils_s3upload

FILE_LOCATION_STRUCTURE = 'service-{}-notify/{}.csv'
TEMP_TAG = 'temp-{user_id}_'
LOGO_LOCATION_STRUCTURE = '{temp}{unique_id}-{filename}'

class S3Client(object):
    def __init__(self, bucket_name, session=None):
        self._bucket_name = bucket_name
        self._session = session

    @property
    def session(self):
        return self._session if self._session else Session()

    @property
    def bucket_name(self):
        return self._bucket_name

    def resource(self, *args, **kwargs):
        return self.session.resource(*args, **kwargs)

    @property
    def s3(self):
        return self.resource('s3')

    @property
    def bucket(self):
        return self.s3.Bucket(self._bucket_name)

    def get_object(self, filename):
        return self.s3.Object(self._bucket_name, filename)

    def delete_object(self, filename):
        return self.get_object(filename).delete()

    def copy_object(self, old_name, new_name, acl=None):
        self.get_object(new_name).copy_from(
            CopySource='{}/{}'.format(self._bucket_name, old_name),
            ACL=acl,
            )


class Clients(object):
    @property
    def logo(self):
        return S3Client(
            current_app.config['LOGO_UPLOAD_BUCKET_NAME'],
            Session(
                current_app.config['AWS_LOGO_ACCESS_KEY_ID'],
                current_app.config['AWS_LOGO_SECRET_ACCESS_KEY']
            )
        )

    @property
    def csv(self):
        return S3Client(current_app.config['CSV_UPLOAD_BUCKET_NAME'])

    @property
    def mou(self):
        return S3Client(current_app.config['MOU_BUCKET_NAME'])

clients = Clients()

def rename_s3_object(client, old_name, new_name, acl=None):
    client.copy_object(old_name, new_name, acl)
    client.delete_object(old_name)

def get_s3_objects_filter_by_prefix(client, prefix):
    return client.bucket.objects.filter(Prefix=prefix)

def get_temp_truncated_filename(filename, user_id):
    return filename[len(TEMP_TAG.format(user_id=user_id)):]

def s3upload(service_id, filedata, region):
    client = clients.csv

    upload_id = str(uuid.uuid4())
    upload_file_name = FILE_LOCATION_STRUCTURE.format(service_id, upload_id)
    utils_s3upload(
        filedata=filedata['data'],
        region=region,
        bucket_name=client.bucket_name,
        file_location=upload_file_name,
        session=client.session
    )
    return upload_id


def s3download(service_id, upload_id):
    client = clients.csv

    contents = ''
    try:
        upload_file_name = FILE_LOCATION_STRUCTURE.format(service_id, upload_id)
        key = client.get_object(upload_file_name)
        contents = key.get()['Body'].read().decode('utf-8')
    except botocore.exceptions.ClientError as e:
        current_app.logger.error("Unable to download s3 file {}".format(
            FILE_LOCATION_STRUCTURE.format(service_id, upload_id)))
        raise e

    return contents


def get_mou(organisation_is_crown):
    client = clients.mou

    bucket = client.bucket_name
    filename = 'crown.pdf' if organisation_is_crown else 'non-crown.pdf'
    attachment_filename = 'Notify.gov.au data sharing and financial agreement{}.pdf'.format(
        '' if organisation_is_crown else ' (non-crown)'
    )
    try:
        key = client.get_object(filename)
        return {
            'filename_or_fp': key.get()['Body'],
            'attachment_filename': attachment_filename,
            'as_attachment': True,
        }
    except botocore.exceptions.ClientError as exception:
        current_app.logger.error("Unable to download s3 file {}/{}".format(
            client.bucket_name, filename
        ))
        raise exception


def upload_logo(filename, filedata, region, user_id):
    client = clients.logo

    upload_file_name = LOGO_LOCATION_STRUCTURE.format(
        temp=TEMP_TAG.format(user_id=user_id),
        unique_id=str(uuid.uuid4()),
        filename=filename
    )

    utils_s3upload(
        filedata=filedata,
        region=region,
        bucket_name=client.bucket_name,
        file_location=upload_file_name,
        content_type='image/png',
        acl='public-read',
        session=client.session
    )

    return upload_file_name


def persist_logo(filename, user_id):
    if filename.startswith(TEMP_TAG.format(user_id=user_id)):
        persisted_filename = get_temp_truncated_filename(
            filename=filename, user_id=user_id)
    else:
        return filename

    rename_s3_object(clients.logo, filename, persisted_filename, acl='public-read')
    return persisted_filename


def delete_temp_files_created_by(user_id):
    client = clients.logo

    for obj in get_s3_objects_filter_by_prefix(client, TEMP_TAG.format(user_id=user_id)):
        client.delete_object(obj.key)


def delete_temp_file(filename):
    if not filename.startswith(TEMP_TAG[:5]):
        raise ValueError('Not a temp file: {}'.format(filename))

    clients.logo.delete_object(filename)
