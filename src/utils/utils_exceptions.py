class UtilsException(Exception):
    pass


class NoPath(UtilsException):
    def __init__(self, path):
        self.url = path

        super().__init__(
            f"There is no  {path} "
        )


class NoYoutubeUrl(UtilsException):
    def __init__(self, url):
        self.url = url

        super().__init__(
            f"There is no youtube url  {url} "
        )
