from prefect import serve
from prefect.server.schemas.schedules import CronSchedule
from app import main_flow

if __name__ == "__main__":
    main_flow.serve(
        name="Daily ETL",
        Schedule=CronSchedule(cron="0 12 * * *", timezone="America/New_York")
    )
