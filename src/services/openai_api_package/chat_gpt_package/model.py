from dataclasses import dataclass




@dataclass
class GPTOptions:
    host: str
    port: int
    api_prefix: str
    single_request_endpoint: str

    @property
    def openai_url_single_request(self) -> str:
        return f"http://{self.host}:{self.port}{self.api_prefix}{self.single_request_endpoint}"

