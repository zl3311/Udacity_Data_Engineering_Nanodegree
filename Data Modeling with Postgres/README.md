# Project Introduction

The goal of this project is to design a Postgres Database Schema of a hypothetical digital music service provider **Sparkify** and to implement the ETL pipeline of song and user activity information. The Database Schema is set to be a Star-style, and raw JSON data files are ingested into the Postgres DB using Python wrapper and SQL query language.

# Project Description

DB schema comprises one fact table and four dimension tables.

Fact table:
- songplays: log data of song plays.
Dimension tables:
- users: user profiles.
- songs: metadata of songs.
- artists: artist profiles.
- time: timestamps of songplays in different units. 


Here's the descriptions of file system in this project.

- data: the folder of raw song and user log data in JSON format.
- create_table.py: script that helps initialize the DBs.
- sql_queries.py: script that creates, schema-designs and drops DBs.
- etl.ipynb, etl.py: (interactive and executable) scripts that ingest the raw data into the DBs.
- test.ipynb: interactive test queries of the created DBs.
- README.md: description markdown.


To run the program:
- Create the databases by running ```python create_table.py```.
- Process data by running ```python etl.py```.
- Evaluate the correctness by querying from the DB inside test.ipynb notebook.