import datetime
from typing import Optional, List

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routers.exceptions import NotFoundError
from src.consumption.models.consumption.history import HistoryDTO, HistoryResultDTO
from src.database.models.consumption.history import HistoryModel
from src.database.models.consumption.summarization import SummaryTexts
from src.database.models.consumption.transcribition import TranscribedTexts
from src.database.repositories.base_repository import BaseRepository


class HistoryRepository(BaseRepository):

    async def add_history(self, user_id: int, unique_id: str, service_source: str, summary_id: int,
                          transcribe_id: int) -> HistoryDTO:
        async with self.db_session_manager.session_scope() as session:
            event = HistoryModel(
                user_id=user_id,
                unique_id=unique_id,
                summary_id=summary_id,
                transcribe_id=transcribe_id,
                service_source=service_source,
                date=datetime.datetime.now()
            )
            session.add(event)
            await session.commit()
            return HistoryDTO.model_validate(event)

    async def update_history(self, user_id: int, unique_id: str, summary_id: Optional[int] = None,
                             transcribe_id: Optional[int] = None) -> HistoryDTO | None:
        async with self.db_session_manager.session_scope() as session:
            query = select(HistoryModel).where(
                HistoryModel.user_id == user_id,
                HistoryModel.unique_id == unique_id)

            result = await session.execute(query)
            event = result.scalars().first()
            if event:
                if summary_id is not None:
                    event.summary_id = summary_id
                if transcribe_id is not None:
                    event.transcribe_id = transcribe_id
                await session.commit()
                return HistoryDTO.model_validate(event)
            return None

    async def check_history(self, user_id: int, source: str) -> bool:
        async with self.db_session_manager.session_scope() as session:
            query = select(HistoryModel). \
                filter(and_(HistoryModel.user_id == user_id, HistoryModel.service_source == source))

            result = await session.execute(query)
            record = result.scalars().all()
            logger.info(f"Проверка ответа истории {len(record) > 0}")
            return len(record) > 0


    async def get_history_by_user_id(
            self,
            user_id: int,
            source: str,
            unique_id: Optional[str] = None
    ) -> list[HistoryResultDTO]:
        async with self.db_session_manager.session_scope() as session:
            query = select(HistoryModel, SummaryTexts, TranscribedTexts).select_from(HistoryModel). \
                join(SummaryTexts, HistoryModel.summary_id == SummaryTexts.id). \
                join(TranscribedTexts, HistoryModel.transcribe_id == TranscribedTexts.id). \
                filter(and_(HistoryModel.user_id == user_id, HistoryModel.service_source == source))

            if unique_id is not None:
                query = query.filter(HistoryModel.unique_id == unique_id)

            result = await session.execute(query)
            records = result.fetchall()
            if not records:
                raise NotFoundError(detail=f"History with user id {user_id} not found")

            history_results = []
            for record in records:
                history_model = record[0]
                summary_texts_model = record[1]
                transcribed_texts_model = record[2]

                history_result = HistoryResultDTO(
                    id=history_model.id,
                    unique_id=history_model.unique_id,
                    user_id=history_model.user_id,
                    summary_text=summary_texts_model.summary_text if summary_texts_model else None,
                    transcribe_text=transcribed_texts_model.text if transcribed_texts_model else None,
                    date=history_model.date
                )
                history_results.append(history_result)
            return history_results

    async def get_history_by_date(self, user_id: int, source: str, date: str) -> list[HistoryResultDTO]:
        async with self.db_session_manager.session_scope() as session:
            query = select(HistoryModel, SummaryTexts, TranscribedTexts).select_from(HistoryModel). \
                join(SummaryTexts, HistoryModel.summary_id == SummaryTexts.id). \
                join(TranscribedTexts, HistoryModel.summary_id == TranscribedTexts.id). \
                filter(HistoryModel.user_id == user_id). \
                filter(HistoryModel.service_source == source). \
                filter(func.date_trunc('day', HistoryModel.date) == func.to_timestamp(date, 'YYYY-MM-DD'))

            result = await session.execute(query)
            records = result.fetchall()
            if not records:
                raise NotFoundError(detail=f"History with user id {user_id} and date {date} not found")

            history_results = []
            for record in records:
                history_model = record[0]
                summary_texts_model = record[1]
                transcribed_texts_model = record[2]

                history_result = HistoryResultDTO(
                    id=history_model.id,
                    user_id=history_model.user_id,
                    summary_text=summary_texts_model.summary_text if summary_texts_model else None,
                    transcribe_text=transcribed_texts_model.text if transcribed_texts_model else None,
                    date=history_model.date
                )
                history_results.append(history_result)

            return history_results
