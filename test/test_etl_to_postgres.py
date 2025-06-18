import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from etl_to_postgres import (
    create_db_engine,
    full_load,
    incremental_load,
    stream_tbl_postgres,
    load_environment,
)

# Sample DataFrames
sample_df = pd.DataFrame({
    'col1': [1, 2],
    'col2': ['a', 'b']
})

sample_df_with_timestamp = pd.DataFrame({
    'col1': [1, 2],
    'col2': ['a', 'b'],
    'Timestamp': [datetime.now() - timedelta(days=1), datetime.now()]
})

# --- Tests ---

def test_load_environment(monkeypatch):
    with patch('etl_to_postgres.load_dotenv') as mock_load_dotenv:
        load_environment('fake_path')
        mock_load_dotenv.assert_called_once_with(dotenv_path='fake_path')

@patch('etl_to_postgres.create_engine')
def test_create_db_engine_success(mock_create_engine, monkeypatch):
    monkeypatch.setenv("DB_USERNAME", "user")
    monkeypatch.setenv("DB_PASSWORD", "pass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "testdb")

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    engine = create_db_engine()
    mock_create_engine.assert_called_once()
    assert engine == mock_engine

def test_create_db_engine_missing_env(monkeypatch):
    monkeypatch.delenv("DB_USERNAME", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

    with pytest.raises(SystemExit):
        create_db_engine()

@patch('etl_to_postgres.pd.read_csv')
@patch('pandas.DataFrame.to_sql')
def test_full_load_success(mock_to_sql, mock_read_csv):
    mock_read_csv.return_value = sample_df
    mock_engine = MagicMock()

    full_load(mock_engine, 'fake.csv', 'table_name')
    mock_read_csv.assert_called_once_with('fake.csv')
    mock_to_sql.assert_called_once_with(
        name='table_name', con=mock_engine, if_exists='replace', index=False
    )

@patch('etl_to_postgres.pd.read_csv')
@patch('pandas.DataFrame.to_sql')
def test_incremental_load_success(mock_to_sql, mock_read_csv):
    mock_read_csv.return_value = sample_df_with_timestamp
    mock_engine = MagicMock()

    # Mock DB max timestamp
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value.execute.return_value.scalar.return_value = datetime.now() - timedelta(days=2)
    mock_engine.connect.return_value = mock_conn

    incremental_load(mock_engine, 'fake.csv', 'table_name')
    mock_read_csv.assert_called_once_with('fake.csv')
    mock_to_sql.assert_called_once_with(
        name='table_name', con=mock_engine, if_exists='append', index=False
    )

@patch('etl_to_postgres.pd.read_csv')
@patch('pandas.DataFrame.to_sql')
def test_incremental_load_no_new_data(mock_to_sql, mock_read_csv):
    old_timestamp = datetime.now() - timedelta(days=2)
    df_old = pd.DataFrame({
        'col1': [1],
        'col2': ['x'],
        'Timestamp': [old_timestamp]
    })

    mock_read_csv.return_value = df_old
    mock_engine = MagicMock()

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value.execute.return_value.scalar.return_value = datetime.now()
    mock_engine.connect.return_value = mock_conn

    incremental_load(mock_engine, 'fake.csv', 'table_name')
    mock_to_sql.assert_not_called()

@patch('etl_to_postgres.pd.read_csv')
@patch('pandas.DataFrame.to_sql')
def test_stream_tbl_postgres_success(mock_to_sql, mock_read_csv):
    mock_read_csv.return_value = sample_df
    mock_engine = MagicMock()

    stream_tbl_postgres(mock_engine, 'fake.csv', 'table_name')
    mock_read_csv.assert_called_once_with('fake.csv')
    mock_to_sql.assert_called_once_with(
        name='table_name', con=mock_engine, if_exists='replace', index=False
    )
