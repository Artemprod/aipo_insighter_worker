import datetime
from typing import Optional

from sqlalchemy import select

from src.consumption.models.consumption.transcribition import TranscribedText
from src.database.models.consumption.transcribition import TranscribedTexts as TranscribedTextModel
from src.database.repositories.base_repository import BaseRepository


class TranscribedTextRepository(BaseRepository):

    async def save(self,
                   text: str,
                   initiator_user_id: int,
                   transcription_date: datetime,
                   transcription_time: datetime,
                   ) -> TranscribedText:
        async with self.db_session_manager.session_scope() as session:
            transcribed_text = TranscribedTextModel(text=text,
                                                    initiator_user_id=initiator_user_id,
                                                    transcription_date=transcription_date,
                                                    transcription_time=transcription_time,
                                                    )
            session.add(transcribed_text)
            await session.commit()

            return TranscribedText(**transcribed_text.to_dict())

    async def get(self, text_id: int) -> Optional[TranscribedText]:
        async with self.db_session_manager.session_scope() as session:
            query = select(TranscribedTextModel).where(TranscribedTextModel.id == text_id)
            results = await session.execute(query)
            result = results.scalars().first()  # Получаем первый объект из результатов запроса
            if result:
                return TranscribedText(**result.to_dict())
            return None

    async def delete(self, text_id: int) -> bool:
        async with self.db_session_manager.session_scope() as session:
            instance = await session.get(TranscribedTextModel, text_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False

