import pytest
import re
import csv
import pandas as pd

def test_file_not_empty():
    with open('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv', 'r') as file:
        content = file.read()
    assert content != '', "The CSV file is empty"

@pytest.mark.validate_csv
@pytest.mark.xfail(reason='Failing the test for testing purpose')
def test_duplicates():
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    duplicate = df[df.duplicated(keep=False)]
    assert duplicate.empty, f"Duplicate rows found: {duplicate}"


@pytest.mark.validate_csv
def test_validate_schema():
    expected_columns = ['id', 'name', 'age', 'email', 'is_active']
    with open('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv', 'r') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        assert headers == expected_columns, f"Expected columns {expected_columns}, but got {headers}"


@pytest.mark.validate_csv
@pytest.mark.skip(reason="Skipping it for testing purpose")
def test_age_column_valid():
    with open('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            age = int(row['age'])
            assert 0 <= age <= 100, f"Age value '{age}' is not a valid integer"


@pytest.mark.validate_csv
def test_email_column_valid():
    with open('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row['email']
            assert re.match(r"[^@]+@[^@]+\.[^@]+", email), f"Email '{email}' is not valid"


@pytest.mark.parametrize("id, is_active", [(1,False),(2,True)])
def test_active_players(id, is_active):
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    match_row = df[df['id'] == id]
    actual_is_active = match_row['is_active'].iloc[0]
    # actual_is_active = actual_is_active.lower() == 'true' if isinstance(actual_is_active, str) else actual_is_active
    assert actual_is_active == is_active, f"Expected is_active value '{is_active}' for id '{id}', but got '{actual_is_active}'"


def test_active_player():
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    match_row = df[df['id'] == 2]
    actual_is_active_player = match_row['is_active'].iloc[0]
    assert actual_is_active_player == 'TRUE', f"Expected is_active value True for id 2, but got '{actual_is_active_player}'"


# ===================== PARAMETRIZE EXAMPLES ====================
@pytest.mark.parametrize("player_id, expected_name", [
    (1, "Michael Jordan"),
    (2, "LeBron James"),
    (3, "Kobe Bryant"),
    (4, "Shaquille O'Neal"),
    (5, "Stephen Curry"),
    (6, "Nikola Jokic")
])
@pytest.mark.smoke
def test_player_names_parametrized(player_id, expected_name):
    """Test player names using parametrize with smoke mark"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    match_row = df[df['id'] == player_id]
    if len(match_row) > 0:
        actual_name = match_row['name'].iloc[0]
        assert actual_name == expected_name, f"Expected {expected_name}, got {actual_name}"


@pytest.mark.parametrize("age", [30, 37, 40, 41, 53, 60])
@pytest.mark.regression
def test_valid_ages_parametrized(age):
    """Test valid ages using parametrize with regression mark"""
    assert 0 <= age <= 100, f"Age {age} is outside valid range"


@pytest.mark.parametrize("id,is_active", [
    (1, False),
    (2, True),
    (5, True),
    (6, True)
])
@pytest.mark.smoke
@pytest.mark.validate_csv
def test_player_status_parametrized(id, is_active):
    """Test player active status using parametrize with multiple marks"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    match_row = df[df['id'] == id]
    if len(match_row) > 0:
        # Convert string to boolean if needed
        actual_status = match_row['is_active'].iloc[0]
        if isinstance(actual_status, str):
            actual_status = actual_status.lower() == 'true'
        assert actual_status == is_active, f"Expected {is_active}, got {actual_status}"


# ==================== SKIP EXAMPLES ====================
@pytest.mark.skip(reason="Not yet implemented - waiting for data validation")
@pytest.mark.smoke
def test_not_implemented_yet():
    """This test is skipped - feature not yet implemented"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    assert True


@pytest.mark.skipif(True, reason="Conditional skip - test environment not ready")
def test_conditional_skip():
    """This test is conditionally skipped"""
    assert True


# ==================== XFAIL EXAMPLES ====================
@pytest.mark.xfail(reason="Known issue - duplicate rows in row 4 and 5")
@pytest.mark.regression
@pytest.mark.critical
def test_no_duplicates_xfail():
    """Test expected to fail - known duplicates in data"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    duplicates = df[df.duplicated(keep=False)]
    assert duplicates.empty, "Duplicate rows exist in data"


@pytest.mark.xfail(reason="Invalid email format in row 7")
def test_strict_email_format_xfail():
    """Test expected to fail - invalid email in test data"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    for idx, row in df.iterrows():
        email = row['email']
        assert re.match(email_pattern, email), f"Invalid email format: {email}"


# ==================== CUSTOM MARK EXAMPLES ====================
@pytest.mark.smoke
@pytest.mark.critical
def test_file_exists_and_readable():
    """Test with smoke and critical custom marks"""
    csv_path = 'C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv'
    import os
    assert os.path.exists(csv_path), f"CSV file not found: {csv_path}"
    with open(csv_path, 'r') as f:
        assert len(f.read()) > 0, "CSV file is empty"


@pytest.mark.integration
@pytest.mark.performance
def test_csv_load_performance():
    """Test with integration and performance custom marks"""
    import time
    start = time.time()
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    load_time = time.time() - start
    assert load_time < 1.0, f"CSV load time {load_time}s exceeded 1 second"
    assert len(df) > 0, "Data should be loaded"


@pytest.mark.regression
@pytest.mark.validate_csv
def test_column_types_regression():
    """Test with regression and validate_csv custom marks"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    expected_columns = ['id', 'name', 'age', 'email', 'is_active']
    assert list(df.columns) == expected_columns, f"Column mismatch: {list(df.columns)}"


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.parametrize("col", ['id', 'name', 'age', 'email', 'is_active'])
def test_column_exists_multi_marks(col):
    """Test with multiple custom marks and parametrize"""
    df = pd.read_csv('C:\\Users\\ThanigaivelSekar\\Desktop\\PytestLearning\\data.csv')
    assert col in df.columns, f"Column '{col}' not found in CSV"

