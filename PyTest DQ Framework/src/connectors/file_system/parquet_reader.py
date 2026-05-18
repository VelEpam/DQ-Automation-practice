import pandas as pd
from pandas import DataFrame


class ParquetReader:
    @staticmethod
    def process(path: str) -> DataFrame:
        return pd.read_parquet(path, engine='pyarrow')
