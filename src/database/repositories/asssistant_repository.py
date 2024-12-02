import datetime
from typing import List

from sqlalchemy import select

from src.api.routers.exceptions import NotFoundError
from src.consumption.models.consumption.asssistant import AIAssistant
from src.database.models.consumption.asssistant import AIAssistant as AIAssistantModel
from src.database.repositories.base_repository import BaseRepository


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

    async def get(self, assistant_id: int) -> AIAssistant:
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
            raise NotFoundError(detail=f"Assistant with id {assistant_id} not found")

    async def get_all(self) -> List[AIAssistant]:
        async with self.db_session_manager.session_scope() as session:
            query = select(AIAssistantModel)
            results = await session.execute(query)
            all_results = results.scalars().all()
            if not all_results:
                raise NotFoundError(detail="Assistants not found")
            return [
                AIAssistant(
                    assistant=result.assistant,
                    name=result.name,
                    assistant_prompt=result.assistant_prompt,
                    user_prompt=result.user_prompt,
                    user_prompt_for_chunks=result.user_prompt_for_chunks,
                    created_at=result.created_at,
                    assistant_id=result.assistant_id
                ) for result in all_results
            ]

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
