import asyncio
from datetime import datetime

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from domain.enteties.buisnes_models import TranscribedText, SummaryText, AIAssistant, WorkerStatus
from domain.enteties.databse_enteties.text_process_models import (TranscribedTexts as TranscribedTextModel,
                                                                  SummaryTexts as SummaryTextsModel,
                                                                  AIAssistant as AIAssistantModel,
                                                                  WorkerStatus as WorkerStatusModel)


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


class BaseRepository:
    def __init__(self, db_session_manager: DatabaseSessionManager):
        self.db_session_manager = db_session_manager


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
                text_record=transcribed_text,
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


class AssistantRepository(BaseRepository):

    async def save(self,
                   assistant: str,
                   name: str,
                   assistant_prompt: str,
                   user_prompt: str,
                   user_prompt_for_chunks: str,
                   created_at: datetime, ) -> AIAssistant:
        async with self.db_session_manager.session_scope() as session:
            ai_assistant = AIAssistantModel(
                assistant=assistant,
                name=name,
                assistant_prompt=assistant_prompt,
                user_prompt=user_prompt,
                user_prompt_for_chunks=user_prompt_for_chunks,
                created_at=created_at
            )
            session.add(ai_assistant)
            await session.commit()
            return AIAssistant(
                assistant=assistant,
                name=name,
                assistant_prompt=assistant_prompt,
                user_prompt=user_prompt,
                user_prompt_for_chunks=user_prompt_for_chunks,
                created_at=created_at,
                assistant_id=ai_assistant.assistant_id
            )

    async def get(self, assistant_id: int) -> Optional[AIAssistant]:
        async with self.db_session_manager.session_scope() as session:
            query = select(AIAssistantModel).where(AIAssistantModel.assistant_id == assistant_id)
            results = await session.execute(query)
            result = results.scalars().first()
            if result:
                return AIAssistant(
                    assistant=result.assistant,
                    name=result.name,
                    assistant_prompt=result.assistant_prompt,
                    user_prompt=result.user_prompt,
                    user_prompt_for_chunks=result.user_prompt_for_chunks,
                    created_at=result.created_at,
                    assistant_id=result.assistant_id
                )
            return None

    # TODO Под вопросом стоит ли передовать объект или так же сделать передачу данных в функцию
    async def update(self, ai_assistant: AIAssistant) -> bool:
        async with self.db_session_manager.session_scope() as session:
            entity = await session.get(AIAssistantModel, ai_assistant.assistant_id)
            if not entity:
                return False
            for key, value in ai_assistant.__dict__.items():
                setattr(entity, key, value)
            await session.commit()
            return True

    async def delete(self, assistant_id: int) -> bool:
        async with self.db_session_manager.session_scope() as session:
            instance = await session.get(AIAssistantModel, assistant_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False


class WorkerStatusRepository(BaseRepository):

    async def save(self,
                   stage_id: int,
                   assistant_id: id,
                   status_id: id,
                   process_id: id,
                   file_id: id,
                   user_id: id,
                   start_time: datetime,
                   end_time: datetime,
                   error_time: datetime,
                   error_message: str,
                   ) -> WorkerStatus:
        async with self.db_session_manager.session_scope() as session:
            worker_status = WorkerStatusModel(
                stage_id=stage_id,
                assistant_id=assistant_id,
                status_id=status_id,
                process_id=process_id,
                file_id=file_id,
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                error_time=error_time,
                error_message=error_message
            )
            session.add(worker_status)
            await session.commit()

            return WorkerStatus(
                stage_id=stage_id,
                assistant_id=assistant_id,
                status_id=status_id,
                process_id=process_id,
                file_id=file_id,
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                error_time=error_time,
                error_message=error_message,
                id=worker_status.id,
            )

    async def get(self, worker_status_id: int) -> Optional[WorkerStatus]:
        async with self.db_session_manager.session_scope() as session:
            result = await session.get(WorkerStatusModel, worker_status_id)
            if result:
                return WorkerStatus(
                    stage_id=result.stage_id,
                    assistant_id=result.assistant_id,
                    status_id=result.status_id,
                    process_id=result.process_id,
                    file_id=result.file_id,
                    user_id=result.user_id,
                    start_time=result.start_time,
                    end_time=result.end_time,
                    error_time=result.error_time,
                    error_message=result.error_message,
                    id=result.id
                )
            return None

    # TODO Под вопросом стоит ли передовать объект или так же сделать передачу данных в функцию
    async def update(self, worker_status: WorkerStatus) -> bool:
        async with self.db_session_manager.session_scope() as session:
            entity = await session.get(WorkerStatusModel, worker_status.id)
            if not entity:
                return False
            for key, value in worker_status.__dict__.items():
                setattr(entity, key, value)
            await session.commit()
            return True

    async def delete(self, worker_status_id: int) -> bool:
        async with self.db_session_manager.session_scope() as session:
            entity = await session.get(WorkerStatusModel, worker_status_id)
            if entity:
                await session.delete(entity)
                await session.commit()
                return True
            return False


if __name__ == "__main__":
    # async def main():
    #     url = "postgresql+asyncpg://postgres:1234@localhost:5432/text_process"
    #     a = DatabaseSessionManager(database_url=url)
    #     r = TranscribedTextRepository(a)
    #     b = SummaryTextRepository(a)
    #
    #     # res = await r.save(text='Текст текст ',
    #     #                    initiator_user_id=123,
    #     #                    file_id=2,
    #     #                    transcription_date=datetime.now(),
    #     #                    transcription_time=datetime.now(),
    #     #                    model_id=2,
    #     #                    language_code='RU',
    #     #                    tags="вася")
    #     # res = await b.save(
    #     #     text="Саммари текст ",
    #     #     transcribed_text_id=3,
    #     #     user_id=123,
    #     #     model_id=1,
    #     #     summary_date=datetime.now(),
    #     #     generation_time=datetime.now(),
    #     #     tokens_requested=123,
    #     #     tokens_generated=123456,
    #     # )
    #     res_g = await b.delete(text_id=2)
    #     print(res_g)
    #     # await r.delete(text_id=1)
    #     # await a.save_summary_text(text="Саммари текст", addressee='123', )
    #     # await a.get_summary_text_by_id(result_id=20)
    async def populate_db(repository):

        test_data = [
            {
                "assistant": "Assistant A",
                "name": "Test Assistant A",
                "assistant_prompt": "How can I assist you today?",
                "user_prompt": "Hello, Assistant",
                "user_prompt_for_chunks": "Hello again, Assistant in chunks",
                "created_at": datetime.now(),
            },
            {
                "assistant": "Assistant B",
                "name": "Test Assistant B",
                "assistant_prompt": "What do you need help with?",
                "user_prompt": "Good morning, Assistant",
                "user_prompt_for_chunks": "Good morning again, Assistant in chunks",
                "created_at": datetime.now(),
            }
        ]

        for data in test_data:
            assistant_object = AIAssistant(**data)  # Создаем объект AIAssistant с данными.
            saved_assistant = await repository.save(
                assistant=assistant_object.assistant,
                name=assistant_object.name,
                assistant_prompt=assistant_object.assistant_prompt,
                user_prompt=assistant_object.user_prompt,
                user_prompt_for_chunks=assistant_object.user_prompt_for_chunks,
                created_at=assistant_object.created_at
            )
            print(f"Saved Assistant: {saved_assistant}")


    # Получаем экземпляр репозитория
    url = "postgresql+asyncpg://postgres:1234@localhost:5432/text_process"
    repository = AssistantRepository(DatabaseSessionManager(database_url=url))

    asyncio.run(populate_db(repository))
