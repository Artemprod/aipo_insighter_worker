class YoutubeLoderException(Exception):
    pass


class YoutubeAudioNotDownloaded(YoutubeLoderException):
    def __init__(self, url, exception_info):
        self.url = url

        super().__init__(
            f"video {url} havn't been downloaded"
            f"additional info {exception_info}"
        )
