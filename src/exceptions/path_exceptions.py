class TelegramServerFileCantBeFoundError(Exception):
    """Exception raised when a file cannot be found on the Telegram server."""

    def __init__(self, message="The requested file cannot be found on the Telegram server."):
        self.message = message
        super().__init__(self.message)


class TelegramServerVolumePathExistingError(Exception):
    """Exception raised when there is an existing path issue on the Telegram server volume."""

    def __init__(self, message="There is an existing path issue on the Telegram server volume."):
        self.message = message
        super().__init__(self.message)
