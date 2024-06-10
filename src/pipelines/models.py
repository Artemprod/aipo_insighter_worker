from dataclasses import dataclass


@dataclass
class PiplineData:
    initiator_user_id: int
    publisher_queue: str
    service_source: str
    assistant_id: int
    file_destination: str
