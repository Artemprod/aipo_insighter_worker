class TranscriptionError(Exception):
    pass


class UnknownTranscriptionError(TranscriptionError):
    def __init__(self, message=None, transcriber=None):
        super().__init__(
            f"Unknow trancribation error {message} was occured  in trancriber {transcriber} "
        )


class APITranscriptionError(TranscriptionError):
    def __init__(self, message=None, transcriber=None):
        super().__init__(
            f"API repsoned an  error: {message}  in trancriber {transcriber} "
        )


class NoResponseFromAssembly(TranscriptionError):
    def __init__(self, exception):
        self.exception = exception

        super().__init__(
            f"No response from assembly API  {exception} "
        )

class NoResponseWhisper(TranscriptionError):
    def __init__(self, exception):
        self.exception = exception

        super().__init__(
            f"No response from whisper API  {exception} "
        )
