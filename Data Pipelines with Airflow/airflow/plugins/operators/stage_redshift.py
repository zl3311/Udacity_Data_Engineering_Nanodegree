from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    
    copy_query = " COPY {} \
        FROM '{}' \
        ACCESS_KEY_ID '{}' \
        SECRET_ACCESS_KEY '{}' \
        FORMAT AS json '{}'; \
        "
    @apply_defaults
    def __init__(self,
             aws_credentials_id="",
             redshift_conn_id="",
             table="",
             s3_bucket="",
             s3_key="",
             json_path="",
             file_type="",
             delimiter=",",
             ignore_headers=1,
             *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.aws_credentials_id = aws_credentials_id
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.log_json_file = json_path
        self.file_type = file_type
        self.delimiter = delimiter
        self.ignore_headers = ignore_headers
        
        
    def execute(self, context):
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        
        s3_path = "s3://{}/{}".format(self.s3_bucket, self.s3_key)
        self.log.info(f"Picking staging file for table {self.table} from location : {s3_path}")
        
        if self.log_json_file != "":
            self.log_json_file = "s3://{}/{}".format(self.s3_bucket, self.log_json_file)
            copy_query = self.copy_query.format(self.table, s3_path, credentials.access_key, credentials.secret_key, self.log_json_file)
        else:
            copy_query = self.copy_query.format(self.table, s3_path, credentials.access_key, credentials.secret_key, 'auto')
        
        
        self.log.info(f"Running copy query : {copy_query}")
        redshift_hook = PostgresHook(postgres_conn_id = self.redshift_conn_id)
        
        redshift_hook.run(copy_query)
        self.log.info(f"Table {self.table} staged successfully!!")
        