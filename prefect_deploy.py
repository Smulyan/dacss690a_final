from app import main

if __name__ == "__main__":
    main.serve(
        name="Daily ETL",
        work_pool_name="default",
        tags=["etl", "daily"]
    )
