import datetime

from sqlalchemy import select

from src.api.routers.exceptions import NotFoundError
from src.consumption.models.consumption.transcribition import TranscribedText
from src.database.models.consumption.transcribition import TranscribedTexts as TranscribedTextModel
from src.database.repositories.base_repository import BaseRepository


class TranscribedTextRepository(BaseRepository):

    async def save(self,
                   text: str,
                   user_id: int,
                   service_source: str,
                   transcription_date: datetime,
                   transcription_time: datetime,
                   ) -> TranscribedText:
        async with self.db_session_manager.session_scope() as session:
            transcribed_text = TranscribedTextModel(text=text,
                                                    transcription_date=transcription_date,
                                                    transcription_time=transcription_time,
                                                    user_id=user_id,
                                                    service_source=service_source,
                                                    )
            session.add(transcribed_text)
            await session.commit()

            return TranscribedText(**transcribed_text.to_dict())

    async def get(self, text_id: int) -> TranscribedText:
        async with self.db_session_manager.session_scope() as session:
            query = select(TranscribedTextModel).where(TranscribedTextModel.id == text_id)
            results = await session.execute(query)
            result = results.scalars().first()  # Получаем первый объект из результатов запроса
            if result:
                return TranscribedText(**result.to_dict())
            raise NotFoundError(detail=f"Transcribed text with id {text_id} not found")

    async def delete(self, text_id: int) -> bool:
        async with self.db_session_manager.session_scope() as session:
            instance = await session.get(TranscribedTextModel, text_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
