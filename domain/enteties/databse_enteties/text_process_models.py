

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, BigInteger, CHAR, Text, DECIMAL, TIME
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

ModelBase = declarative_base()


class Currencies(ModelBase):
    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(CHAR(3), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code
        }


class Pricing(ModelBase):
    __tablename__ = 'pricing'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    cost_per_token = Column(DECIMAL(10, 4), nullable=False)
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)

    model = relationship('Models')
    currency = relationship('Currencies')

    def to_dict(self):
        return {
            'id': self.id,
            'model_id': self.model_id,
            'cost_per_token': str(self.cost_per_token),
            'currency_id': self.currency_id
        }


class SummaryTexts(ModelBase):
    __tablename__ = 'summary_texts'

    id = Column(BigInteger, primary_key=True)
    summary_text = Column(Text, nullable=False)
    transcribed_text_id = Column(BigInteger, ForeignKey('transcribed_texts.id'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    summary_date = Column(TIMESTAMP, nullable=False)
    generation_time = Column(TIME, nullable=False)
    tokens_requested = Column(Integer, nullable=False)
    tokens_generated = Column(Integer, nullable=False)

    transcribed_text = relationship('TranscribedTexts')
    model = relationship('Models')

    def to_dict(self):
        return {
            'id': self.id,
            'summary_text': self.summary_text,
            'transcribed_text_id': self.transcribed_text_id,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'summary_date': self.summary_date.isoformat(),
            'generation_time': self.generation_time.isoformat(),
            'tokens_requested': self.tokens_requested,
            'tokens_generated': self.tokens_generated
        }


class Formats(ModelBase):
    __tablename__ = 'formats'

    id = Column(Integer, primary_key=True)
    format_name = Column(String(255), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'format_name': self.format_name}


class Sources(ModelBase):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    source_name = Column(String(255), nullable=False)
    domain = Column(String(255))

    def to_dict(self):
        return {'id': self.id, 'source_name': self.source_name, 'domain': self.domain}


class Models(ModelBase):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(255))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'version': self.version}


class Files(ModelBase):
    __tablename__ = 'files'

    id = Column(BigInteger, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    link = Column(String(255), nullable=False)
    format_id = Column(Integer, ForeignKey('formats.id'), nullable=False)
    duration = Column(INTERVAL)
    file_size = Column(BigInteger)
    owner_id = Column(BigInteger, nullable=False)
    upload_date = Column(TIMESTAMP, nullable=False)

    source = relationship('Sources')
    format = relationship('Formats')

    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'link': self.link,
            'format_id': self.format_id,
            'duration': str(self.duration),  # Convert INTERVAL to string for easier handling
            'file_size': self.file_size,
            'owner_id': self.owner_id,
            'upload_date': self.upload_date.isoformat()
        }


class TranscribedTexts(ModelBase):
    __tablename__ = 'transcribed_texts'

    id = Column(BigInteger, primary_key=True)
    text = Column(Text, nullable=False)
    initiator_user_id = Column(BigInteger, nullable=False)
    file_id = Column(BigInteger, ForeignKey('files.id'), nullable=False)
    transcription_date = Column(TIMESTAMP, nullable=False)
    transcription_time = Column(TIMESTAMP, nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    language_code = Column(CHAR(2))
    tags = Column(Text)

    file = relationship('Files')
    model = relationship('Models')

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'initiator_user_id': self.initiator_user_id,
            'file_id': self.file_id,
            'transcription_date': self.transcription_date.isoformat(),
            'transcription_time': self.transcription_time.isoformat(),
            'model_id': self.model_id,
            'language_code': self.language_code,
            'tags': self.tags
        }


class AIAssistant(ModelBase):
    __tablename__ = "ai_assistants"

    assistant_id = Column(Integer, primary_key=True, autoincrement=True)
    assistant = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    assistant_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    user_prompt_for_chunks = Column(Text)
    created_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<AIAssistant(assistant_id={self.assistant_id}, assistant='{self.assistant}', name='{self.name}')>"


class Status(ModelBase):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True)
    status_name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Status(id={self.id}, status_name='{self.status_name}')>"


class Stage(ModelBase):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True)
    stage_name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Stage(id={self.id}, stage_name='{self.stage_name}')>"


class WorkerStatus(ModelBase):
    __tablename__ = "worker_statuses"

    id = Column(Integer, primary_key=True)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    assistant_id = Column(Integer, ForeignKey('ai_assistants.assistant_id'),
                          nullable=False)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    process_id = Column(BigInteger)
    file_id = Column(BigInteger, ForeignKey('files.id'), nullable=False)
    user_id = Column(BigInteger)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    error_time = Column(TIMESTAMP)
    error_message = Column(Text)

    stage = relationship("Stage")
    status = relationship("Status")

    def __repr__(self):
        return (f"<WorkerStatus(id={self.id}, stage_id={self.stage_id}, assistant_id={self.assistant_id}, "
                f"status_id={self.status_id}, process_id={self.process_id}, file_id={self.file_id})>")
