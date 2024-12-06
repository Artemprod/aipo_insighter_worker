import os

import pytest

from container import settings
from src.file_manager.s3.s3_client import S3Client
from src.file_manager.s3.s3_file_manager import S3FileManager


@pytest.mark.asyncio
@pytest.mark.parametrize("s3_url", [
    'https://b8ffac09-9e42-4827-b4b2-22f1081ea55c.selstorage.ru/posting-label-58515541-0006-2.pdf'
])
async def test_load(s3_url, monkeypatch):
    async def mock_download_file_from_url(url: str, destination_path: str) -> None:
        # Mocking download_file_from_url to simulate file download
        with open(destination_path, 'wb') as file:
            file.write(b'test content')

    monkeypatch.setattr(S3FileManager, 'download_file_from_url', staticmethod(mock_download_file_from_url))

    destination_filename = os.path.join(os.getcwd(), s3_url.split('/')[-1])
    await S3FileManager()._load(s3_url, destination_filename)

    assert os.path.exists(destination_filename)
    os.remove(destination_filename)  # Clean up after test


@pytest.mark.parametrize("file_name", [
    'test_files/some_txt_file.txt'
])
@pytest.mark.asyncio
async def test_upload_file_and_delete_file(file_name):
    import requests
    client = S3Client(
        access_key=settings.selectel.access_key,
        secret_key=settings.selectel.secret_key,
        endpoint_url=settings.selectel.endpoint_url,
        bucket_name=settings.selectel.bucket_name
    )
    object_name = await client.upload_file(file_path=file_name)
    url = await client.generate_presigned_url(object_name)
    response = requests.get(url)
    assert response.status_code == 200
    await client.delete_file(object_name)
    response = requests.get(url)
    assert response.status_code == 404
