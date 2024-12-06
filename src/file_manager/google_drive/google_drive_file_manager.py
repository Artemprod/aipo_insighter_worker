import re

import gdown

from src.file_manager.base_file_manager import BaseFileManager
from src.utils.wrappers import async_wrap


class GoogleDriveFileManager(BaseFileManager):

    @async_wrap
    def _load(self, url: str, output_path: str) -> str:
        gdown.download(url=url, output=output_path, fuzzy=True)
        return output_path

    def _extract_file_name_from_url(self, url: str) -> str | None:
        pattern = r"(?:/d/|uc\?id=)([a-zA-Z0-9_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
