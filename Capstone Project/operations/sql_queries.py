import configparser

config = configparser.ConfigParser()
config.read('./aws/credentials.cfg')
ROLE_ARN = config.get("IAM_ROLE","ARN")

# GET
COUNTRY_DATA = config.get("S3","COUNTRY_DATA")
I94_DATA = config.get("S3","I94_DATA")
STATE_DEMO_DATA = config.get("S3","STATE_DATA")
VISA_DATA = config.get("S3","VISA_DATA")

# DROP
staging_immigration_table_drop = "DROP TABLE IF EXISTS staging_immigration"
staging_state_demo_table_drop = "DROP TABLE IF EXISTS staging_state_demo"
staging_country_table_drop = "DROP TABLE IF EXISTS staging_country"
staging_visa_table_drop = "DROP TABLE IF EXISTS staging_visa"

immigration_table_drop = "DROP TABLE IF EXISTS fact_immigration"
country_table_drop = "DROP TABLE IF EXISTS dim_country"
state_demo_table_drop = "DROP TABLE IF EXISTS dim_state_demo"
visa_table_drop = "DROP TABLE IF EXISTS dim_visa"

# CREATE STAGING
staging_immigration_table_create = ("""CREATE TABLE IF NOT EXISTS staging_immigration (
                                           cicid INT,
                                           i94cit INT,
                                           i94res INT,
                                           i94port VARCHAR,
                                           i94mode INT,
                                           i94addr VARCHAR,
                                           gender VARCHAR,
                                           visatype VARCHAR                                 
                                    )""")

staging_state_demo_table_create = ("""CREATE TABLE IF NOT EXISTS staging_state_demo (
                                        state_code VARCHAR,
                                        male_population INT,
                                        female_population INT,
                                        total_population INT,
                                        number_of_veterans INT
                                    )""")

staging_country_table_create = ("""CREATE TABLE IF NOT EXISTS staging_country (
                                        country_code INT, 
                                        country_name VARCHAR
                                    )""")

staging_visa_table_create = ("""CREATE TABLE IF NOT EXISTS staging_visa (
                                        visa_type VARCHAR,
                                        visa_def VARCHAR    
                                    )""")

# CREATE FACT AND DIMENSION TABLES
immigration_table_create = ("""CREATE TABLE IF NOT EXISTS fact_immigration (
                                        cicid INT PRIMARY KEY, 
                                        i94cit INT,
                                        i94res INT,
                                        i94port VARCHAR,
                                        i94mode INT,
                                        i94addr VARCHAR,
                                        gender VARCHAR,
                                        visatype VARCHAR,
                                        CONSTRAINT fk_country_cit
                                            FOREIGN KEY(i94cit) 
                                                REFERENCES dim_country(country_code),
                                        CONSTRAINT fk_country_res
                                            FOREIGN KEY(i94res) 
                                                REFERENCES dim_country(country_code),
                                        CONSTRAINT fk_visatype
                                            FOREIGN KEY(visatype) 
                                                REFERENCES dim_visa(visa_type),
                                        CONSTRAINT fk_state
                                            FOREIGN KEY(i94addr) 
                                                REFERENCES dim_state_demo(state_code)
                                    )""")

country_table_create = ("""CREATE TABLE IF NOT EXISTS dim_country (
                                country_code INT PRIMARY KEY, 
                                country_name VARCHAR) 
                            diststyle all""")

state_demo_table_create = ("""CREATE TABLE IF NOT EXISTS dim_state_demo (
                                    state_code VARCHAR PRIMARY KEY,
                                    male_population INT,
                                    female_population INT,
                                    total_population INT,
                                    number_of_veterans INT)
                                diststyle all""")

visa_table_create = ("""CREATE TABLE IF NOT EXISTS dim_visa (
                            visa_type VARCHAR PRIMARY KEY, 
                            visa_def VARCHAR)
                        diststyle all""")


# COPY 
staging_immigration_copy = ("""COPY staging_immigration 
                               FROM '{}'
                               IAM_ROLE '{}'
                               FORMAT AS PARQUET;
                            """).format(I94_DATA, ROLE_ARN)

staging_state_demo_copy = ("""COPY staging_state_demo
                                FROM '{}'
                                IAM_ROLE '{}'
                                FORMAT AS PARQUET;
                             """).format(STATE_DEMO_DATA, ROLE_ARN)

staging_country_copy = ("""COPY staging_country
                              FROM '{}'
                              IAM_ROLE '{}'
                              FORMAT AS PARQUET;
                           """).format(COUNTRY_DATA, ROLE_ARN)

staging_visa_copy = ("""COPY staging_visa
                              FROM '{}'
                              IAM_ROLE '{}'
                              FORMAT AS PARQUET;
                           """).format(VISA_DATA, ROLE_ARN)

# INSERT

immigration_table_insert = ("""INSERT INTO fact_immigration (cicid, i94cit, i94res, i94port, i94mode, i94addr, gender, visatype)
                                    SELECT cicid, i94cit, i94res, i94port, i94mode, i94addr, gender, visatype
                                    FROM staging_immigration
                            """)

country_table_insert = ("""INSERT INTO dim_country (country_code, country_name)
                                SELECT country_code, country_name
                                FROM staging_country
                        """)

state_table_insert = ("""INSERT INTO dim_state_demo (state_code, male_population, female_population, total_population, number_of_veterans)
                                SELECT state_code, male_population, female_population, total_population, number_of_veterans
                                FROM staging_state_demo
                      """)


visa_table_insert = ("""INSERT INTO dim_visa (visa_type, visa_def)
                                SELECT visa_type, visa_def
                                FROM staging_visa
                      """)

# QUERY LISTS

drop_table_queries = [staging_immigration_table_drop, staging_state_demo_table_drop, staging_country_table_drop, 
                      staging_visa_table_drop, immigration_table_drop, country_table_drop, state_demo_table_drop, visa_table_drop]

create_table_queries = [staging_immigration_table_create, staging_state_demo_table_create, staging_country_table_create, 
                        staging_visa_table_create, immigration_table_create, country_table_create, state_demo_table_create,visa_table_create]

copy_table_queries = [staging_immigration_copy, staging_state_demo_copy, staging_country_copy, staging_visa_copy]

insert_table_queries = [immigration_table_insert, country_table_insert, state_table_insert, visa_table_insert]