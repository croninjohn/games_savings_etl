# Recent Gaming Deals Tracker

This is a data pipeline that pulls recent gaming bargains from [Cheap Shark](https://www.cheapshark.com/) via their API. The data ingested in turn supports [this interactive dashboard](http://18.212.173.53:3000/public/dashboard/cda4da01-2386-433a-b4ce-c3ae2ec5ee75). (Check it out!)

[![dashboard_preview](images/dashboard_preview.png)](http://18.212.173.53:3000/public/dashboard/cda4da01-2386-433a-b4ce-c3ae2ec5ee75)
*okay, okay, this is just a screenshot. But it's also a link to the live dashboard!*

## Architecture

![Architecture Diagram](images/games_savings_arch.png)

All of the computing is performed within a small EC2 instance, while the warehouse used to store the data is a RDS PostgreSQL database. A single [Python script](src/api_etl.py) (automated, for now, via a simple cron job) queries two API endpoints ([stores](https://apidocs.cheapshark.com/#f0bc20fe-688b-68d9-df27-22d6f6441849) for information about digital game vendors and [deals](https://apidocs.cheapshark.com/#c33f57dd-3bb3-3b1f-c454-08cab413a115) for the details of all the different games on sale), performs some light transformation on the data it receives, then writes that data to the DB. A [view](sql_scripts/dashboard_view.sql) instantiated within the relevant schema combines the two tables into a single clean dataset that the Metabase dashboard linked above draws from to populate itself. Both the ETL script and the dashboard are run via Docker containers running on the EC2 instance; for convenience, the dashboard stores its metadata (RDS login details, dashboard details, etc.) on the EC2 instance via a bind mount.



## Future Refinements

As I get the time, I plan to return to this project and make some of the following additions:
* Automate data ingestion, transformation, and clean-up with Airflow.
* Switch the dashboard's metadata storage from bind mount to Docker volume.
* Incorporate further endpoints (from this source or others) to expand functionality.



