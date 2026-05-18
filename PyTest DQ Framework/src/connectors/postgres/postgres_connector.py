
from typing import Optional

import psycopg2
import pandas as pd
from pandas import DataFrame


class PostgresConnectorContextManager:
    def __init__(self, db_host: str, db_name: str, db_user: str, db_password: str, db_port: int = 5432):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.connection: Optional[psycopg2.extensions.connection] = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.connection:
            self.connection.close()

    def get_data_sql(self, sql: str) -> DataFrame:
        try:
            return pd.read_sql(sql, self.connection)
        except Exception as e:
            raise Exception(f"Failed to receive data from DB: {e}")


