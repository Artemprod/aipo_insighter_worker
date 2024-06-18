# async def populate_db(repository):
#     test_data = [
#         {
#             "assistant": "Assistant A",
#             "name": "Test Assistant A",
#             "assistant_prompt": "How can I assist you today?",
#             "user_prompt": "Hello, Assistant",
#             "user_prompt_for_chunks": "Hello again, Assistant in chunks",
#             "created_at": datetime.now(),
#         },
#         {
#             "assistant": "Assistant B",
#             "name": "Test Assistant B",
#             "assistant_prompt": "What do you need help with?",
#             "user_prompt": "Good morning, Assistant",
#             "user_prompt_for_chunks": "Good morning again, Assistant in chunks",
#             "created_at": datetime.now(),
#         }
#     ]
#
#     for data in test_data:
#         assistant_object = AIAssistant(**data)  # Создаем объект AIAssistant с данными.
#         saved_assistant = await repository.save(
#             assistant=assistant_object.assistant,
#             name=assistant_object.name,
#             assistant_prompt=assistant_object.assistant_prompt,
#             user_prompt=assistant_object.user_prompt,
#             user_prompt_for_chunks=assistant_object.user_prompt_for_chunks,
#             created_at=assistant_object.created_at
#         )
#         print(f"Saved Assistant: {saved_assistant}")
#
#
# # Получаем экземпляр репозитория
# url = "postgresql+asyncpg://postgres:1234@localhost:5432/procees"
# repository = AssistantRepository(DatabaseSessionManager(database_url=url))
#
# asyncio.run(populate_db(repository))
