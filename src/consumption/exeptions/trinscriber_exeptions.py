class TranscriptionError(Exception):
    pass


class NoResponseFromAssembly(TranscriptionError):
    def __init__(self, exception):
        self.exception = exception

        super().__init__(
            f"No response from assembly API  {exception} "
        )
