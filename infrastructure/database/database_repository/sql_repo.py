import asyncio
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from domain.enteties.databse_enteties.sql_ent import TranscribedText, SummaryText


class ResultsRepository:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_size=5,  # Минимальное количество соединений
            max_overflow=10,  # Количество соединений, которые создаются сверх pool_size, если все соединения заняты
            pool_timeout=30,
            # Время ожидания в секундах, прежде чем будет выброшено исключение, если нет доступных соединений
            pool_recycle=1800,
            # Время в секундах, через которое соединение будет заменено на новое, чтобы избежать проблем с устареванием соединений
        )
        self.engine = create_async_engine(database_url, echo=True)
        # Название изменено на async_session_factory для соответствия стилю
        self.async_session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, class_=AsyncSession)

    @asynccontextmanager
    async def session_scope(self) -> Any:
        """
        Асинхронный контекстный менеджер для сессий.
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def save_transcribed_text(self, text: str, addressee: str) -> None:
        """
        Асинхронное сохранение транскрибированного текста в базу данных.
        """
        async with self.session_scope() as session:
            new_result = TranscribedText(text=text, addressee=addressee)
            session.add(new_result)
        return new_result.id

    async def get_transcribed_text_by_id(self, result_id: int) -> TranscribedText:
        async with self.session_scope() as session:
            query = select(TranscribedText).where(TranscribedText.id == result_id)
            results = await session.execute(query)
            result = results.scalars().first()  # Получаем первый объект из результатов запроса
            return result

    async def save_summary_text(self, text: str, addressee: str) -> None:

        async with self.session_scope() as session:
            new_result = SummaryText(text=text, addressee=addressee)
            session.add(new_result)
        return new_result.id

    async def get_summary_text_by_id(self, result_id: int) -> SummaryText:
        async with self.session_scope() as session:
            query = select(SummaryText).where(SummaryText.id == result_id)
            results = await session.execute(query)
            result = results.scalars().first()  # Получаем первый объект из результатов запроса
            return result


if __name__ == "__main__":
    async def main():
        url = "postgresql+asyncpg://postgres:1234@localhost:5432/postgres"
        a = ResultsRepository(database_url=url)
        await a.save_transcribed_text(text="Транскрибированый текст", addressee='123',)
        await a.save_summary_text(text="Саммари текст", addressee='123',)



    asyncio.run(main())
