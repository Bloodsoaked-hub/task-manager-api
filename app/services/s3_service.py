import os
import boto3

from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status

from app.core.config import Settings

settings = Settings()


class S3service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

    def upload_rag_document(self, file: UploadFile) -> str:
        try:
            s3_key = f"documents/{file.filename}"
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                s3_key,
                ExtraArgs={"ContentType": file.content_type},
            )
            return s3_key
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AWS S3 upload error: {str(e)}",
            )

    def read_rag_document(self, s3_key: str) -> str:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response["Body"].read().decode("utf-8")
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found in S3: {str(e)}",
            )
