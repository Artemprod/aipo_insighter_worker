# import datetime
# from typing import Optional
#
# from src.database.models.consumption.conusumption_status import WorkerStatus as WorkerStatusModel
# from src.consumption.models.consumption.conusumption_status import WorkerStatus
# from src.database.repositories.base_repository import BaseRepository
#
#
# class WorkerStatusRepository(BaseRepository):
#
#     async def save(self,
#                    stage_id: int,
#                    assistant_id: id,
#                    status_id: id,
#                    process_id: id,
#                    file_id: id,
#                    user_id: id,
#                    start_time: datetime,
#                    end_time: datetime,
#                    error_time: datetime,
#                    error_message: str,
#                    ) -> WorkerStatus:
#         async with self.db_session_manager.session_scope() as session:
#             worker_status = WorkerStatusModel(
#                 stage_id=stage_id,
#                 assistant_id=assistant_id,
#                 status_id=status_id,
#                 process_id=process_id,
#                 file_id=file_id,
#                 user_id=user_id,
#                 start_time=start_time,
#                 end_time=end_time,
#                 error_time=error_time,
#                 error_message=error_message
#             )
#             session.add(worker_status)
#             await session.commit()
#
#             return WorkerStatus(
#                 stage_id=stage_id,
#                 assistant_id=assistant_id,
#                 status_id=status_id,
#                 process_id=process_id,
#                 file_id=file_id,
#                 user_id=user_id,
#                 start_time=start_time,
#                 end_time=end_time,
#                 error_time=error_time,
#                 error_message=error_message,
#                 id=worker_status.id,
#             )
#
#     async def get(self, worker_status_id: int) -> Optional[WorkerStatus]:
#         async with self.db_session_manager.session_scope() as session:
#             result = await session.get(WorkerStatusModel, worker_status_id)
#             if result:
#                 return WorkerStatus(
#                     stage_id=result.stage_id,
#                     assistant_id=result.assistant_id,
#                     status_id=result.status_id,
#                     process_id=result.process_id,
#                     file_id=result.file_id,
#                     user_id=result.user_id,
#                     start_time=result.start_time,
#                     end_time=result.end_time,
#                     error_time=result.error_time,
#                     error_message=result.error_message,
#                     id=result.id
#                 )
#             return None
#
#     # TODO Под вопросом стоит ли передовать объект или так же сделать передачу данных в функцию
#     async def update(self, worker_status: WorkerStatus) -> bool:
#         async with self.db_session_manager.session_scope() as session:
#             entity = await session.get(WorkerStatusModel, worker_status.id)
#             if not entity:
#                 return False
#             for key, value in worker_status.__dict__.items():
#                 setattr(entity, key, value)
#             await session.commit()
#             return True
#
#     async def delete(self, worker_status_id: int) -> bool:
#         async with self.db_session_manager.session_scope() as session:
#             entity = await session.get(WorkerStatusModel, worker_status_id)
#             if entity:
#                 await session.delete(entity)
#                 await session.commit()
#                 return True
#             return False
