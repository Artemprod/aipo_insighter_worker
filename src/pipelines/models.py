from dataclasses import dataclass


@dataclass
class PiplineData:
    unique_id:str
    initiator_user_id: int
    publisher_queue: str
    service_source: str
    assistant_id: int
    file_destination: str
