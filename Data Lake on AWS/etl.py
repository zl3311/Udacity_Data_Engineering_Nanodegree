import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql import functions as F
from pyspark.sql import types as T

config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config.get("AWS",'AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY']=config.get("AWS",'AWS_SECRET_ACCESS_KEY')


def create_spark_session():
    """
    function that creates spark session.
    """
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    ETL function that process song data.
    :param spark: current Spark session.
    :param input_data: directory of input data.
    :param output_data: directory of output data.
    """
    # get filepath to song data file
    song_data = input_data + "song_data/*/*/*"
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = (
        df.select(
            'song_id', 'title', 'artist_id', 'year', 'duration'
        ).drop_duplicates() 
    )
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(output_data+"song.parquet", mode="overwrite", partitionBy=["year", "artist_id"])

    # extract columns to create artists table
    artists_table = (
        df.select(
            'artist_id',
            col('artist_name').alias('name'),
            col('artist_location').alias('location'),
            col('artist_latitude').alias('latitude'),
            col('artist_longitude').alias('longitude')
        ).drop_duplicates()
    )
    
    # write artists table to parquet files
    artists_table.write.parquet(output_data+"artist.parquet", mode="overwrite")


def process_log_data(spark, input_data, output_data):
    """
    ETL function that process log data.
    :param spark: current Spark session.
    :param input_data: directory of input data.
    :param output_data: directory of output data.
    """
    # get filepath to log data file
    log_data = input_data + "log_data/*/*"

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.where(df.page=='NextSong')

    # extract columns for users table    
    users_table = (
        df.select(
            col('userId').alias('user_id'),
            col('firstName').alias('first_name'),
            col('lastName').alias('last_name'),
            col('gender').alias('gender'),
            col('level').alias('level')
        ).drop_duplicates()
    )
    
    # write users table to parquet files
    users_table.write.parquet(output_data+"users.parquet", mode="overwrite")

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: datetime.utcfromtimestamp(int(x)/1000), TimestampType())
    df = df.withColumn("start_time", get_timestamp("ts"))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: F.to_date(x), TimestampType())
    df = df.withColumn("hour",hour("start_time"))\
           .withColumn("day",dayofmonth("start_time"))\
           .withColumn("week",weekofyear("start_time"))\
           .withColumn("month",month("start_time"))\
           .withColumn("year",year("start_time"))\
           .withColumn("weekday",dayofweek("start_time"))
    
    # extract columns to create time table
    time_table = (
        df.select("ts","start_time","hour", "day", "week", "month", "year", "weekday").distinct()
    ).drop_duplicates()
    
    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(output_data+"time.parquet", mode="overwrite", partitionBy=["year", "month"])

    # read in song data to use for songplays table
    song_df = spark.read.parquet(output_data+"songs.parquet")

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = (
        df.withColumn("songplay_id", F.monotonically_increasing_id())
          .join(song_df, song_df.title == df.song)
          .select(
            col('start_time').alias('start_time'),
            col('userId').alias('user_id'),
            col('level').alias('level'),
            col('song_id').alias('song_id'),
            col('artist_id').alias('artist_id'),
            col('sessionId').alias('session_id'),
            col('location').alias('location'),
            col('userAgent').alias('user_agent'),
            col('year').alias('year'),
            col('month').alias('month')
          ).drop_duplicates()
    )

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.parquet(output_data + "songplays.parquet", mode="overwrite", partitionBy=["year", "month"])


def main():
    """
    Main function
    """
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://udacity-dend/output/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
