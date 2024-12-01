from dataclasses import dataclass

from src.api.schemas import ServiceSources


@dataclass
class PiplineData:
    unique_id: str
    initiator_user_id: int
    publisher_queue: str
    service_source: ServiceSources
    assistant_id: int
    file_destination: str
    user_prompt: str
