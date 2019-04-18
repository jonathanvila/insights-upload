import boto3
import os
import logging

from utils import mnm

from botocore.exceptions import ClientError

logger = logging.getLogger("upload-service")

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', None)

# S3 buckets
PERM = os.getenv('S3_PERM', 'insights-upload-perm-test')
REJECT = os.getenv('S3_REJECT', 'insights-upload-rejected')

s3 = boto3.client('s3',
                  endpoint_url=S3_ENDPOINT_URL,
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


@mnm.uploads_s3_write_seconds.time()
def write(data, dest, uuid):
    s3.upload_file(data, dest, uuid)
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': dest,
                                            'Key': uuid}, ExpiresIn=86400)
    logger.info("Data written to s3", extra={"request_id": uuid})
    return url


@mnm.uploads_s3_copy_seconds.time()
def copy(src, dest, uuid):
    copy_src = {'Bucket': src,
                'Key': uuid}
    s3.copy(copy_src, dest, uuid)
    s3.delete_object(Bucket=src, Key=uuid)
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': dest,
                                            'Key': uuid}, ExpiresIn=86400)
    logger.info("Data copied to %s bucket", dest, extra={"request_id": uuid})
    return url


@mnm.uploads_s3_get_url_seconds.time()
def get_url(bucket, uuid):
    url = s3.generate_presigned_url("get_object",
                                    Params={"Bucket": bucket,
                                            "Key": uuid}, ExpiresIn=86400)
    return url


@mnm.uploads_s3_ls_seconds.time()
def ls(src, uuid):
    try:
        result = s3.head_object(Bucket=src, Key=uuid)
        return result
    except ClientError:
        return {'ResponseMetadata': {'HTTPStatusCode': 404}}
