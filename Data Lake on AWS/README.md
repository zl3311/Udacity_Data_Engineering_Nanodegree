# Project Summary

In this project, I created an ETL pipeline extracting data from a **data lake** hosted on **Amazon S3**, transforming it using **Spark**, and outputing it back to S3 in **parquet** format.

# Project Stucture

- ```etl.py```: pipeline functions that perform ETL transformations.
- ```dl.cfg```: AWS credential.
- ```README.md```: markdown file of project description.

# How-to-Run

1. Config ```dl.cfg``` credential correctly.
2. run ```python etl.py``` in the terminal.