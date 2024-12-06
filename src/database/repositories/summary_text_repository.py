import datetime

from sqlalchemy import select

from src.api.routers.exceptions import NotFoundError
from src.database.models.consumption.summarization import SummaryTexts as SummaryTextsModel
from src.consumption.models.consumption.summarization import SummaryTextScheme
from src.database.repositories.base_repository import BaseRepository


class SummaryTextRepository(BaseRepository):

    async def save(self,
                   text: str,
                   user_id: int,
                   service_source:str,
                   summary_date: datetime,
                   ) -> SummaryTextScheme:
        async with self.db_session_manager.session_scope() as session:
            summary_text = SummaryTextsModel(summary_text=text,
                                             user_id=user_id,
                                             summary_date=summary_date,
                                             service_source=service_source,
                                             )
            session.add(summary_text)
            await session.commit()

            return SummaryTextScheme.model_validate(summary_text)

    async def get(self, text_id: int) -> SummaryTextScheme:
        async with self.db_session_manager.session_scope() as session:
            query = select(SummaryTextsModel).where(SummaryTextsModel.id == text_id)
            results = await session.execute(query)
            result = results.scalars().first()
            if result:
                return SummaryTextScheme.model_validate(result)
            raise NotFoundError(detail=f"Transcribed text with id {text_id} not found")

    async def delete(self, text_id: int):
        async with self.db_session_manager.session_scope() as session:
            instance = await session.get(SummaryTextsModel, text_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
