from dataclasses import dataclass
from datetime import datetime
from typing import Optional





@dataclass
class WorkerStatus:
    stage_id: int
    assistant_id: int
    status_id: int
    process_id: int
    file_id: int
    user_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error_time: Optional[datetime]
    error_message: Optional[str]
    id: Optional[int] = None
