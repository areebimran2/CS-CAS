import uuid

import boto3
from django.conf import settings


def _get_client():
    return boto3.client('s3',
                        endpoint_url=settings.S3_ENDPOINT_URL,
                        aws_access_key_id=settings.S3_ACCESS_KEY,
                        aws_secret_access_key=settings.S3_SECRET_KEY,
                        )


def upload_file(file, folder):
    """
    Upload a Django UploadedFile object to S3.
    Returns the public URL of the stored object

    :param file: Django UploadedFile object
    :param folder: folder path within the bucket to store the file (e.g. 'ships/...')
    """
    client = _get_client()
    ext = file.name.rsplit('.', 1)[-1]
    key = f'{folder}/{uuid.uuid4().hex}.{ext}'  # object key in s3 (e.g. 'ships/{ship_id}/3f8a...c1.jpg')

    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=file.read(),
        ContentType=file.content_type,
    )

    return f'{settings.S3_PUBLIC_URL}/{key}'

def delete_file(url):
    """
    Delete a file from S3 using public URL.
    """
    client = _get_client()
    key = url.rsplit(f'{settings.S3_PUBLIC_URL}/', 1)[-1]

    client.delete_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key
    )

