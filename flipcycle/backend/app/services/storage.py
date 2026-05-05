from uuid import uuid4
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from app.core.config import get_settings

settings = get_settings()


def s3_client():
    return boto3.client(
        's3',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id.get_secret_value() if settings.aws_access_key_id else None,
        aws_secret_access_key=settings.aws_secret_access_key.get_secret_value() if settings.aws_secret_access_key else None,
    )


async def upload_file(file: UploadFile, prefix: str) -> dict[str, str | int]:
    if not settings.s3_bucket:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='S3_BUCKET is not configured')
    content = await file.read()
    key = f"{prefix}/{uuid4()}-{file.filename}"
    try:
        s3_client().put_object(Bucket=settings.s3_bucket, Key=key, Body=content, ContentType=file.content_type)
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='S3 upload failed') from exc
    url = f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
    return {'key': key, 'url': url, 'size': len(content), 'mime_type': file.content_type or 'application/octet-stream'}
