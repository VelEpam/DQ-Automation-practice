import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            duplicates = df[df.duplicated(subset=column_names, keep=False)]
        else:
            duplicates = df[df.duplicated(keep=False)]
        assert duplicates.empty, (
            f"Duplicate records found ({len(duplicates)} rows):\n{duplicates}"
        )

    @staticmethod
    def check_count(df1, df2):
        count1 = len(df1)
        count2 = len(df2)
        assert count1 == count2, (
            f"Row count mismatch: source has {count1} rows, target has {count2} rows"
        )

    @staticmethod
    def check_full_data_set(df1, df2, columns=None, sort_columns=None):
        if columns:
            df1 = df1[columns].copy()
            df2 = df2[columns].copy()
        else:
            df1 = df1.copy()
            df2 = df2.copy()

        if sort_columns:
            df1 = df1.sort_values(by=sort_columns).reset_index(drop=True)
            df2 = df2.sort_values(by=sort_columns).reset_index(drop=True)

        pd.testing.assert_frame_equal(df1, df2, check_like=True, check_dtype=False)

    @staticmethod
    def check_dataset_is_not_empty(df):
        assert not df.empty, "Dataset is empty"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        cols = column_names if column_names else df.columns.tolist()
        for col in cols:
            null_count = df[col].isnull().sum()
            assert null_count == 0, (
                f"Column '{col}' has {null_count} null value(s)"
            )
