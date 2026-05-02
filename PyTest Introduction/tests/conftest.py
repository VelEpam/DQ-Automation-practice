import pytest
import pandas as pd

# Fixture to read the CSV file
@pytest.fixture(params=['C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv'], scope='session')
def read_csv(request):
    df= pd.read_csv(request.param)
    return df

def test_file_not_empty(read_csv):
    assert not read_csv.empty, "The CSV file is empty"


# Fixture to validate the schema of the file
@pytest.fixture(scope='session')
def schema_validator():
    def validate(actual_schema, expected_schema):
        assert actual_schema == expected_schema, \
            f"Expected columns {expected_schema}, but got {actual_schema}"
        return True
    return validate



def test_with(schema_validator):
    expected_schema = ['id', 'name', 'age', 'email', 'is_active']
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    actual_headers = df.columns.tolist()
    
    assert schema_validator(actual_headers, expected_schema)


# ==================== PARAMETRIZE TESTS ====================
@pytest.mark.parametrize("id, expected_name", [
    (1, "Michael Jordan"),
    (2, "LeBron James"),
    (3, "Kobe Bryant")
])
@pytest.mark.smoke
def test_player_names_parametrized(id, expected_name):
    """Test player names using parametrize"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    match_row = df[df['id'] == id]
    actual_name = match_row['name'].iloc[0]
    assert actual_name == expected_name, f"Expected {expected_name}, got {actual_name}"


@pytest.mark.parametrize("age", [30, 37, 40, 41, 53, 60])
@pytest.mark.regression
def test_valid_ages_parametrized(age):
    """Test that all ages are within valid range using parametrize"""
    assert 0 <= age <= 100, f"Age {age} is outside valid range"


# ==================== SKIP TESTS ====================
@pytest.mark.skip(reason="Feature not yet implemented")
@pytest.mark.smoke
def test_future_feature():
    """Test that is skipped - feature not implemented yet"""
    assert True


@pytest.mark.skipif(True, reason="Skipping based on condition")
def test_conditional_skip():
    """Test that is conditionally skipped"""
    assert True


# ==================== XFAIL TESTS ====================
@pytest.mark.xfail(reason="Known issue - duplicate rows exist in data")
@pytest.mark.regression
def test_duplicate_detection_xfail():
    """Test that is expected to fail - there are known duplicates"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    duplicates = df[df.duplicated(keep=False)]
    assert duplicates.empty, "Duplicates found in data"


@pytest.mark.xfail(reason="Email validation issue in row 7")
@pytest.mark.validate_csv
def test_email_format_xfail():
    """Test that is expected to fail - invalid email in data"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    import re
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    for idx, row in df.iterrows():
        assert re.match(email_pattern, row['email']), f"Invalid email: {row['email']}"


# ==================== CUSTOM MARK TESTS ====================
@pytest.mark.smoke
@pytest.mark.integration
def test_csv_file_exists_custom_marks():
    """Test with custom marks - smoke and integration"""
    import os
    csv_path = 'C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv'
    assert os.path.exists(csv_path), f"CSV file not found: {csv_path}"


@pytest.mark.regression
@pytest.mark.validate_csv
def test_data_load_regression():
    """Test with custom regression and validate_csv marks"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    assert len(df) > 0, "Data should not be empty"
    assert df.shape[1] == 5, "Should have 5 columns"


@pytest.mark.performance
def test_csv_load_performance():
    """Test with custom performance mark"""
    import time
    start = time.time()
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    end = time.time()
    load_time = end - start
    assert load_time < 1, f"CSV load time {load_time}s exceeded 1 second"


# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(config, items):
    for item in items:
        # Check if test has any explicit user-defined marks (exclude parametrize)
        user_marks = [mark for mark in item.iter_markers() if mark.name not in ['parametrize', 'xfail', 'skip']]
        
        # If no user-defined marks exist, add 'unmarked' mark
        if not user_marks:
            item.add_marker(pytest.mark.unmarked)

