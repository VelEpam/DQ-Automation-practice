import pytest
from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.data_quality.data_quality_validation_library import DataQualityLibrary
from src.connectors.file_system.parquet_reader import ParquetReader


def pytest_addoption(parser):
    parser.addoption("--db_host", action="store", default="localhost", help="Database host")
    parser.addoption("--db_port", action="store", default="5432", help="Database port")
    parser.addoption("--db_name", action="store", default="mydatabase", help="Database name")
    parser.addoption("--db_user", action="store", default=None, help="Database user")
    parser.addoption("--db_password", action="store", default=None, help="Database password")
    parser.addoption(
        "--parquet_base_path",
        action="store",
        default="/parquet_data",
        help="Base path for parquet files"
    )


@pytest.fixture(scope='session')
def db_connection(request):
    db_host = request.config.getoption("--db_host")
    db_port = int(request.config.getoption("--db_port"))
    db_name = request.config.getoption("--db_name")
    db_user = request.config.getoption("--db_user")
    db_password = request.config.getoption("--db_password")

    if not db_user or not db_password:
        pytest.fail(
            "Database credentials are required. Provide --db_user and --db_password."
        )

    try:
        with PostgresConnectorContextManager(
            db_host=db_host,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            db_port=db_port
        ) as db_connector:
            yield db_connector
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnectorContextManager: {e}")


@pytest.fixture(scope='session')
def parquet_reader():
    return ParquetReader()


@pytest.fixture(scope='session')
def data_quality_library():
    return DataQualityLibrary()


@pytest.fixture(scope='session')
def parquet_base_path(request):
    return request.config.getoption("--parquet_base_path")
