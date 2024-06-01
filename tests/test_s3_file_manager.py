import os

import pytest

from src.file_manager.s3.s3_file_loader import S3FileLoader


@pytest.mark.parametrize("s3_url", [
    'https://b8ffac09-9e42-4827-b4b2-22f1081ea55c.selstorage.ru/posting-label-58515541-0006-2.pdf'
])
def test_load(s3_url, monkeypatch):
    def mock_download_file_from_url(url: str, destination_path: str) -> None:
        # Mocking download_file_from_url to simulate file download
        with open(destination_path, 'wb') as file:
            file.write(b'test content')

    monkeypatch.setattr(S3FileLoader, 'download_file_from_url', mock_download_file_from_url)

    file_loader = S3FileLoader(s3_url)
    file_loader.load()

    current_directory = os.getcwd()
    destination_filename = os.path.join(current_directory, s3_url.split('/')[-1])
    assert os.path.exists(destination_filename)
    os.remove(destination_filename)  # Clean up after test
