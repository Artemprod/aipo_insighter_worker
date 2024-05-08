import asyncio
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager


class DatabaseSessionManager:
    def __init__(self, database_url: str):
        # Настройка асинхронного движка SQLAlchemy с параметрами пула соединений
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )

        # Создание фабрики для асинхронных сессий
        self.async_session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, class_=AsyncSession)

    @asynccontextmanager
    async def session_scope(self):
        """
        Асинхронный контекстный менеджер для сессий SQLAlchemy.
        Управляет транзакциями: автоматически коммитит или откатывает транзакции в случае ошибки.
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

class TranscribedTextRepository:

    def __init__(self, db_session_manager: DatabaseSessionManager):
        self.db_session_manager = db_session_manager

    async def save(self):
        ...

    async def get(self):
        ...

    async def update(self):
        ...

    async def delete(self):
        ...


class ResultsRepository:
    def __init__(self, db_session_manager: DatabaseSessionManager):
        self.db_session_manager = db_session_manager

    async def save_transcribed_text(self, text: str, addressee: str):
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
            print()
            print(result)
            return result


if __name__ == "__main__":
    async def main():
        url = "postgresql+asyncpg://postgres:1234@localhost:5432/postgres"
        a = ResultsRepository(database_url=url)
        await a.save_transcribed_text(text="Транскрибированый текст", addressee='123', )
        await a.save_summary_text(text="Саммари текст", addressee='123', )
        await a.get_summary_text_by_id(result_id=20)


    asyncio.run(main())
