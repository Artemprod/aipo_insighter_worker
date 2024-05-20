from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import relationship

from src.database.models.base_model import ModelBase

class WorkerStatus(ModelBase):
    __tablename__ = "worker_statuses"
    id = Column(Integer, primary_key=True)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    assistant_id = Column(Integer, ForeignKey('ai_assistants.assistant_id'), nullable=False)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    process_id = Column(BigInteger)
    file_id = Column(BigInteger, ForeignKey('files.id'), nullable=False)
    user_id = Column(BigInteger)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    error_time = Column(TIMESTAMP)
    error_message = Column(Text)


    status = relationship("Status")
    stage = relationship("Stage")

    def __repr__(self):
        return (f"<WorkerStatus(id={self.id}, stage_id={self.stage_id}, assistant_id={self.assistant_id}, "
                f"status_id={self.status_id}, process_id={self.process_id}, file_id={self.file_id})>")
