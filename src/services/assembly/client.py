import assemblyai as aai


class AssemblyClient:

    def __init__(self, api_key):
        aai.settings.api_key = api_key
        self.TranscriptionConfig = aai.TranscriptionConfig
        self.Transcriber = aai.Transcriber
