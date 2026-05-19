import pytest


SOURCE_QUERY = """
SELECT
    f.facility_type,
    CONCAT(p.first_name, ' ', p.last_name) AS full_name,
    SUM(v.treatment_cost) AS sum_treatment_cost
FROM
    visits v
JOIN
    facilities f
    ON f.id = v.facility_id
JOIN
    patients p
    ON p.id = v.patient_id
GROUP BY
    f.facility_type,
    full_name
"""

PARQUET_DATASET = "patient_sum_treatment_cost_per_facility_type"
KEY_COLUMNS = ["facility_type", "full_name"]
DATA_COLUMNS = ["facility_type", "full_name", "sum_treatment_cost"]


@pytest.fixture(scope='module')
def source_data(db_connection):
    return db_connection.get_data_sql(SOURCE_QUERY)


@pytest.fixture(scope='module')
def target_data(parquet_reader, parquet_base_path):
    target_path = f"{parquet_base_path}/{PARQUET_DATASET}"
    return parquet_reader.process(target_path)


@pytest.mark.patient_sum_treatment_cost
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.patient_sum_treatment_cost
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.patient_sum_treatment_cost
def test_check_no_duplicates(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data, column_names=KEY_COLUMNS)


@pytest.mark.patient_sum_treatment_cost
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(target_data, column_names=DATA_COLUMNS)


@pytest.mark.patient_sum_treatment_cost
def test_check_full_data_set(source_data, target_data, data_quality_library):
    data_quality_library.check_full_data_set(
        source_data,
        target_data[DATA_COLUMNS],
        columns=DATA_COLUMNS,
        sort_columns=KEY_COLUMNS
    )
