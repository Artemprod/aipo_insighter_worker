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



