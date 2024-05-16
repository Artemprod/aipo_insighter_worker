import datetime
from typing import Optional

from sqlalchemy import select

from src.database.models.consumption.summarization import SummaryTexts as SummaryTextsModel
from src.consumption.models.consumption.summarization import SummaryText
from src.database.repositories.base_repository import BaseRepository


class SummaryTextRepository(BaseRepository):

    async def save(self,
                   text: str,
                   transcribed_text_id: int,
                   user_id: int,
                   model_id: int,
                   summary_date: datetime,
                   generation_time: datetime,
                   tokens_requested: int,
                   tokens_generated: int) -> SummaryText:
        async with self.db_session_manager.session_scope() as session:
            summary_text = SummaryTextsModel(summary_text=text,
                                             transcribed_text_id=transcribed_text_id,
                                             user_id=user_id,
                                             model_id=model_id,
                                             summary_date=summary_date,
                                             generation_time=generation_time,
                                             tokens_requested=tokens_requested,
                                             tokens_generated=tokens_generated)
            session.add(summary_text)
            await session.commit()

            return SummaryText(
                summary_text=text,
                transcribed_text_id=transcribed_text_id,
                user_id=user_id,
                model_id=model_id,
                summary_date=summary_date,
                generation_time=generation_time,
                tokens_requested=tokens_requested,
                tokens_generated=tokens_generated,
                id=summary_text.id,

            )

    async def get(self, text_id: int) -> Optional[SummaryText]:
        async with self.db_session_manager.session_scope() as session:
            query = select(SummaryTextsModel).where(SummaryTextsModel.id == text_id)
            results = await session.execute(query)
            result = results.scalars().first()
            if result:
                return SummaryText(
                    summary_text=result.summary_text,
                    transcribed_text_id=result.transcribed_text_id,
                    user_id=result.user_id,
                    model_id=result.model_id,
                    summary_date=result.summary_date,
                    generation_time=result.generation_time,
                    tokens_requested=result.tokens_requested,
                    tokens_generated=result.tokens_generated,
                    id=result.id,

                )
            return None

    async def delete(self, text_id: int):
        async with self.db_session_manager.session_scope() as session:
            instance = await session.get(SummaryTextsModel, text_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
