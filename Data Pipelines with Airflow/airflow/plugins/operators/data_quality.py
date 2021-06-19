from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
             redshift_conn_id="",
             tables=[],
             *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.tables = tables
        
    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)
        
        for t in self.tables:
            self.log.into(f"Checking Data Quality for {t} table")
            records = redshift_hook.get_records(f"SELECT COUNT(*) FROM {t}")
            if len(records[0]) < 1 or len(records) < 1:
                raise ValueError(f"Data quality check failed: Table {t} has no results")
            num_records = records[0][0]
            if num_records < 1:
                raise ValueError(f"Data quality check failed: Table {t} has 0 rows.")
            self.log.info('Data Quality check passed with {records[0][0]} records.')