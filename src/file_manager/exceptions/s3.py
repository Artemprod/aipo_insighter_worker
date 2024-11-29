class S3LoderException(Exception):
    pass


class S3FileNotDownloaded(S3LoderException):
    def __init__(self, url,exception_info):
        self.url = url

        super().__init__(
            f"file {url} hasn't been downloaded"
            f"additional info {exception_info}"
        )
