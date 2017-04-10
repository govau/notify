import boto
from moto import mock_s3
from notifications_utils.s3 import s3upload


def test_s3upload_save_file_to_bucket():
    mock = mock_s3()
    mock.start()
    s3upload(filedata='some file data',
             region='eu-west-1',
             bucket_name='some_bucket',
             file_location='some_file_location')
    conn = boto.connect_s3()
    assert conn.get_bucket('some_bucket').get_key('some_file_location').get_contents_as_string() == b'some file data'

    mock.stop()
