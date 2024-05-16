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
                   file_id: int,
                   transcription_date: datetime,
                   transcription_time: datetime,
                   model_id: int,
                   language_code: str,
                   tags: str) -> TranscribedText:
        async with self.db_session_manager.session_scope() as session:
            transcribed_text = TranscribedTextModel(text=text,
                                                    initiator_user_id=initiator_user_id,
                                                    file_id=file_id,
                                                    transcription_date=transcription_date,
                                                    transcription_time=transcription_time,
                                                    model_id=model_id,
                                                    language_code=language_code,
                                                    tags=tags)
            session.add(transcribed_text)
            await session.commit()

            return TranscribedText(
                id=transcribed_text.id,
                text=text,
                initiator_user_id=initiator_user_id,
                file_id=file_id,
                transcription_date=transcription_date,
                transcription_time=transcription_time,
                model_id=model_id,
                language_code=language_code,
                tags=tags,
            )

    async def get(self, text_id: int) -> Optional[TranscribedText]:
        async with self.db_session_manager.session_scope() as session:
            query = select(TranscribedTextModel).where(TranscribedTextModel.id == text_id)
            results = await session.execute(query)
            result = results.scalars().first()  # Получаем первый объект из результатов запроса
            if result:
                return TranscribedText(
                    text=result.text,
                    initiator_user_id=result.initiator_user_id,
                    file_id=result.file_id,
                    transcription_date=result.transcription_date,
                    transcription_time=result.transcription_time,
                    model_id=result.model_id,
                    language_code=result.language_code,
                    tags=result.tags,
                )
            return None

    async def delete(self, text_id: int) -> bool:
        async with self.db_session_manager.session_scope() as session:
            instance = await session.get(TranscribedTextModel, text_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False

