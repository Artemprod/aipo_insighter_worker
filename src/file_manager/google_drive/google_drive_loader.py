import gdown

from src.file_manager.interface import IBaseFileLoader
from src.utils.wrappers import async_wrap


class GoogleDriveFileLoader(IBaseFileLoader):

    @async_wrap
    def load(self, g_drive_url: str, output_path: str) -> str:
        gdown.download(url=g_drive_url, output=output_path, fuzzy=True)
        return output_path
