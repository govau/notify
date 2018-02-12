import urllib

import botocore
from boto3 import resource
from flask import current_app


def s3upload(filedata, region, bucket_name, file_location, content_type='binary/octet-stream', tags=None):
    _s3 = resource('s3')
    contents = filedata

    exists = True
    try:
        _s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
        else:
            current_app.logger.error(
                "Unable to create s3 bucket {}".format(bucket_name))
            raise e

    if not exists:
        _s3.create_bucket(Bucket=bucket_name,
                          CreateBucketConfiguration={'LocationConstraint': region})

    upload_file_name = file_location
    key = _s3.Object(bucket_name, upload_file_name)

    put_args = {
        'Body': contents,
        'ServerSideEncryption': 'AES256',
        'ContentType': content_type
    }

    if tags:
        tags = urllib.parse.urlencode(tags)
        put_args['Tagging'] = tags

    key.put(**put_args)
