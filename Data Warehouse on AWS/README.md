# Project Summary

The project performs datawarehouding for a hypothetical digital music company in the cloud environment of AWS. The volume of data is big (>1M records), thus it requires efficient ways of designing database schema and structure.

Specifically, I build ETL pipelines of 
1. extracting raw data from Amazon S3
2. staging it in Amazon Redshift
3. further transforming the data into dimensional and fact tables for efficient analysis purpose by partitioning the entire dataset using sorting and distribution keys.

# How-to Run
1. Setup ```dwh.cfg``` AWS credentials.
2. Run ```python create_table.py``` in the terminal to create the databases.
3. Run ```python etl.py``` in the terminal to ingest and process the data.

# Project Structure
- ```create_tables.py```: meta functions of create databases.
- ```etl.py```: meta functions of data processing pipelines.
- ```sql_queries.py```: AWS/database setup and data injection/query languages of SQL with Python wrapper.
