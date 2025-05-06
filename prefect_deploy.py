from app import main

if __name__ == "__main__":
    main.deploy(
        name="Daily ETL",
        work_pool_name="default",
        tags=["etl", "daily"]
    )
