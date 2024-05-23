from dataclasses import dataclass


@dataclass
class PiplineData:
    initiator_user_id: int | str
    publisher_queue:str
