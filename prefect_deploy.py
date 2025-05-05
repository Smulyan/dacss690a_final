from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from app import main

# Define and register the deployment
Deployment.build_from_flow(
    flow=main,
    name="Daily ETL",
    schedule=(CronSchedule(cron="0 12 * * *", timezone="America/New_York")),  # Runs daily at noon ET
    work_pool_name="default",
    tags=["etl", "daily"]
).apply()
