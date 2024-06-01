import asyncio
from contextlib import asynccontextmanager

import aiofiles
from aiobotocore.config import AioConfig
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from types_aiobotocore_s3.client import S3Client as S3ClientType


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": 'ru-1',
            "config": AioConfig(s3={'addressing_style': 'virtual'})
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> S3ClientType:
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_path: str):
        object_name = file_path.split("/")[-1]
        try:
            async with self.get_client() as client:
                client: S3ClientType
                async with aiofiles.open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=await file.read(),
                    )
                print(f"File {object_name} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                client: S3ClientType
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def download_file(self, object_name: str, destination_path: str):
        try:
            async with self.get_client() as client:
                client: S3ClientType
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                async with aiofiles.open(destination_path, "wb") as file:
                    await file.write(data)
                print(f"File {object_name} downloaded to {destination_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")

    async def get_all_object(self):
        try:
            async with self.get_client() as client:
                client: S3ClientType
                response = await client.list_objects_v2(Bucket=self.bucket_name)
                if 'Contents' in response:
                    return [obj['Key'] for obj in response['Contents']]
                return []
        except ClientError as e:
            print(f"Error listing objects: {e}")
            return []

    async def get_bucket_access_control_list(self):
        try:
            async with self.get_client() as client:
                client: S3ClientType
                response = await client.get_bucket_acl(Bucket=self.bucket_name)
                return response
        except ClientError as e:
            print(f"Error getting bucket ACL: {e}")

    async def generate_presigned_url(self, key: str) -> str:
        try:
            async with self.get_client() as client:
                client: S3ClientType
                response = await client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': key},
                    ExpiresIn=1488
                )
                return response
        except Exception as err:
            print(err)


async def main():
    ...


if __name__ == "__main__":
    asyncio.run(main())
