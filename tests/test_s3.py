from notifications_utils.s3 import s3upload


def test_s3upload_save_file_to_bucket(mocker):
    mocked = mocker.patch('notifications_utils.s3.resource')
    s3upload(filedata='some file data',
             region='eu-west-1',
             bucket_name='some_bucket',
             file_location='some_file_location')
    mocked_put = mocked.return_value.Object.return_value.put
    mocked_put.assert_called_once_with(Body='some file data', ServerSideEncryption='AES256')
