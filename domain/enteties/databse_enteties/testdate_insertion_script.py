from datetime import datetime, timedelta

from domain.enteties.databse_enteties.text_process_models import Currencies, Formats, Sources, Models, AIAssistant, \
    Files, Status, WorkerStatus, Stage

if __name__ == '__main__':

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker


    DATABASE_URL = ****
    engine = create_async_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


    async def insert_data():
        async with Session() as session:
            # Начало транзакции
            async with session.begin():
                # Вставка данных в таблицу Currencies
                currencies = [Currencies(name="Dollar", code="USD"), Currencies(name="Euro", code="EUR"),
                              Currencies(name="Yen", code="JPY")]
                session.add_all(currencies)

                # Вставка данных в таблицу Formats
                formats = [Formats(format_name="PDF"), Formats(format_name="DOCX"), Formats(format_name="TXT")]
                session.add_all(formats)

                # Вставка данных в таблицу Sources
                sources = [Sources(source_name="Online", domain="internet.com"),
                           Sources(source_name="Local", domain="localhost")]
                session.add_all(sources)

            # Подтверждение вставки начальных данных
            await session.commit()

            # Таблицы с зависимостями
            async with session.begin():
                # Данные для моделей
                models = [Models(name="Model 1", version="1.0"), Models(name="Model 2", version="2.0")]
                session.add_all(models)

                # Данные для AI Assistants
                assistants = [AIAssistant(assistant="Alpha", name="Альфа", assistant_prompt="Help with scheduling",
                                          user_prompt="Arrange my meetings")]
                session.add_all(assistants)

                # Данные для файлов, зависят от источника и формата
                files = [
                    Files(source_id=1, link="file://document1.pdf", format_id=1, duration=timedelta(seconds=30), file_size=1024,
                          owner_id=1, upload_date=datetime.now())]
                session.add_all(files)

            # Подтверждение вставки данных с зависимостями
            await session.commit()

            # Продолжение с более сложными зависимостями
            async with session.begin():
                # Данные для статусов и этапов работ
                statuses = [Status(status_name="Received"), Status(status_name="Processing"),
                            Status(status_name="Completed")]
                stages = [Stage(stage_name="Start"), Stage(stage_name="Middle"), Stage(stage_name="End")]
                session.add_all(statuses + stages)

            await session.commit()

            # Данные для WorkerStatus, который зависит от ai_assistants, files, statuses и stages
            async with session.begin():
                worker_statuses = [
                    WorkerStatus(stage_id=1, assistant_id=3, status_id=1, process_id=123, file_id=1, user_id=1,
                                 start_time=datetime.now(), end_time=datetime.now(), error_time=None,
                                 error_message=None)]
                session.add_all(worker_statuses)

            # Финальное подтверждение вставки всех данных
            await session.commit()


    async def main():
        await insert_data()

    import asyncio

    asyncio.run(main())
