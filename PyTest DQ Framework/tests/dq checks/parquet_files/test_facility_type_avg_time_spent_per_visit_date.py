
import pytest
import pandas as pd


SOURCE_QUERY = """
SELECT
    f.facility_type,
    v.visit_timestamp::date AS visit_date,
    ROUND(AVG(v.duration_minutes), 2) AS avg_time_spent
FROM
    visits v
JOIN
    facilities f
    ON f.id = v.facility_id
GROUP BY
    f.facility_type,
    v.visit_timestamp::date
"""

PARQUET_DATASET = "facility_type_avg_time_spent_per_visit_date"
KEY_COLUMNS = ["facility_type", "visit_date"]
DATA_COLUMNS = ["facility_type", "visit_date", "avg_time_spent"]


@pytest.fixture(scope='module')
def source_data(db_connection):
    return db_connection.get_data_sql(SOURCE_QUERY)


@pytest.fixture(scope='module')
def target_data(parquet_reader, parquet_base_path):
    target_path = f"{parquet_base_path}/{PARQUET_DATASET}"
    return parquet_reader.process(target_path)


@pytest.mark.facility_type_avg_time_spent
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.facility_type_avg_time_spent
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.facility_type_avg_time_spent
def test_check_no_duplicates(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data, column_names=KEY_COLUMNS)


@pytest.mark.facility_type_avg_time_spent
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(target_data, column_names=DATA_COLUMNS)


@pytest.mark.facility_type_avg_time_spent
def test_check_full_data_set(source_data, target_data, data_quality_library):
    source = source_data.copy()
    target = target_data[DATA_COLUMNS].copy()

    source["visit_date"] = pd.to_datetime(source["visit_date"]).dt.normalize()
    target["visit_date"] = pd.to_datetime(target["visit_date"]).dt.normalize()

    data_quality_library.check_full_data_set(
        source,
        target,
        columns=DATA_COLUMNS,
        sort_columns=KEY_COLUMNS
    )
