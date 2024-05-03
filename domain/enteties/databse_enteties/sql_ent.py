from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TranscribedText(Base):
    __tablename__ = "transcribed_text"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)
    addressee = Column(String)

    def __repr__(self):
        return "<TranscribedText(text='%s', addressee='%s'>" % (
            self.text,
            self.addressee,

        )

class SummaryText(Base):

    __tablename__ = "summary_text"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)
    addressee = Column(String)

    def __repr__(self):
        return "<TranscribedText(text='%s', addressee='%s'>" % (
            self.text,
            self.addressee,

        )