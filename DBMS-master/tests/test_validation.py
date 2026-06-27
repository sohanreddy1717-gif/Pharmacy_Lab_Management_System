"""
tests/test_validation.py
------------------------
Unit tests for the Pharmacy Lab Management System.

Two layers of testing:
  1. Pure validation logic — no DB needed, fast, always reliable.
  2. DB-layer unit tests — mock mysql.connector so tests run without
     a real MySQL server (using unittest.mock.patch + MagicMock).

Run with:  pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime


# ===========================================================================
# Section 1 — Pure Validation Logic
# (Mirrors the helpers in db_tasks.py so these tests run without imports)
# ===========================================================================

def is_valid_age(age: int) -> bool:
    return isinstance(age, int) and age > 0


def is_valid_gender(gender: str) -> bool:
    return gender.upper() in ('M', 'F')


def is_valid_contact(contact: str) -> bool:
    return contact.isdigit() and 7 <= len(contact) <= 15


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_non_empty(value: str) -> bool:
    return bool(value.strip())


# ---------------------------------------------------------------------------
# Age Tests
# ---------------------------------------------------------------------------

class TestAgeValidation:
    def test_valid_age(self):
        assert is_valid_age(25) is True

    def test_age_one(self):
        assert is_valid_age(1) is True

    def test_age_zero_invalid(self):
        assert is_valid_age(0) is False

    def test_negative_age_invalid(self):
        assert is_valid_age(-5) is False

    def test_large_age_valid(self):
        assert is_valid_age(120) is True

    def test_float_not_valid(self):
        assert is_valid_age(25.5) is False  # type: not int


# ---------------------------------------------------------------------------
# Gender Tests
# ---------------------------------------------------------------------------

class TestGenderValidation:
    def test_male_uppercase(self):
        assert is_valid_gender("M") is True

    def test_female_uppercase(self):
        assert is_valid_gender("F") is True

    def test_male_lowercase(self):
        assert is_valid_gender("m") is True

    def test_female_lowercase(self):
        assert is_valid_gender("f") is True

    def test_invalid_gender_x(self):
        assert is_valid_gender("X") is False

    def test_invalid_gender_empty(self):
        assert is_valid_gender("") is False

    def test_invalid_gender_word(self):
        assert is_valid_gender("Male") is False


# ---------------------------------------------------------------------------
# Contact Tests
# ---------------------------------------------------------------------------

class TestContactValidation:
    def test_valid_10_digit(self):
        assert is_valid_contact("9876543210") is True

    def test_valid_7_digit(self):
        assert is_valid_contact("1234567") is True

    def test_valid_15_digit(self):
        assert is_valid_contact("123456789012345") is True

    def test_too_short(self):
        assert is_valid_contact("123456") is False

    def test_too_long(self):
        assert is_valid_contact("1234567890123456") is False

    def test_with_letters(self):
        assert is_valid_contact("98765abcde") is False

    def test_with_spaces(self):
        assert is_valid_contact("9876 543210") is False

    def test_with_dashes(self):
        assert is_valid_contact("987-654-3210") is False

    def test_empty(self):
        assert is_valid_contact("") is False


# ---------------------------------------------------------------------------
# Date Tests
# ---------------------------------------------------------------------------

class TestDateValidation:
    def test_valid_date(self):
        assert is_valid_date("2024-06-15") is True

    def test_valid_date_2000(self):
        assert is_valid_date("2000-01-01") is True

    def test_slash_format_invalid(self):
        assert is_valid_date("15/06/2024") is False

    def test_no_separator_invalid(self):
        assert is_valid_date("20240615") is False

    def test_invalid_month(self):
        assert is_valid_date("2024-13-01") is False

    def test_invalid_day(self):
        assert is_valid_date("2024-02-30") is False

    def test_empty(self):
        assert is_valid_date("") is False

    def test_text(self):
        assert is_valid_date("abc-xyz-123") is False

    def test_partial(self):
        assert is_valid_date("2024-06") is False


# ---------------------------------------------------------------------------
# Non-Empty String Tests
# ---------------------------------------------------------------------------

class TestNonEmptyValidation:
    def test_valid_string(self):
        assert is_non_empty("John") is True

    def test_whitespace_only(self):
        assert is_non_empty("   ") is False

    def test_empty_string(self):
        assert is_non_empty("") is False

    def test_string_with_surrounding_spaces(self):
        assert is_non_empty("  John Doe  ") is True


# ===========================================================================
# Section 2 — DB-layer Unit Tests (with mocked mysql.connector)
#
# We patch 'db_tasks.get_connection' so no real MySQL server is needed.
# Each test sets up a MagicMock cursor/connection, then verifies that
# db_tasks.py calls the right SQL with the right parameters.
# ===========================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db_tasks


def make_mock_conn(fetchone_return=None, fetchall_return=None, rowcount=1):
    """
    Factory: returns a (mock_conn, mock_cursor) pair pre-wired for common
    scenarios so each test only overrides what it actually cares about.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = fetchone_return
    mock_cursor.fetchall.return_value = fetchall_return or []
    mock_cursor.rowcount = rowcount
    mock_cursor.lastrowid = 42

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    return mock_conn, mock_cursor


# ---------------------------------------------------------------------------
# retrieve_patient — DB layer
# ---------------------------------------------------------------------------

class TestRetrievePatient:

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_int", return_value=1)
    def test_patient_found_executes_correct_sql(self, mock_input, mock_get_conn, capsys):
        mock_conn, mock_cursor = make_mock_conn(
            fetchone_return=(1, "Alice", 30, "F", "9876543210")
        )
        mock_get_conn.return_value = mock_conn

        db_tasks.retrieve_patient()

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM Patients WHERE patient_id = %s", (1,)
        )
        captured = capsys.readouterr()
        assert "Alice" in captured.out

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_int", return_value=999)
    def test_patient_not_found_prints_error(self, mock_input, mock_get_conn, capsys):
        mock_conn, mock_cursor = make_mock_conn(fetchone_return=None)
        mock_get_conn.return_value = mock_conn

        db_tasks.retrieve_patient()

        captured = capsys.readouterr()
        assert "No patient found" in captured.out


# ---------------------------------------------------------------------------
# delete_patient — DB layer
# ---------------------------------------------------------------------------

class TestDeletePatient:

    @patch("db_tasks.get_connection")
    @patch("db_tasks.confirm_commit", return_value=True)
    @patch("db_tasks.get_int", return_value=5)
    def test_delete_patient_no_reports_calls_delete(
        self, mock_int, mock_commit, mock_get_conn, capsys
    ):
        mock_conn, mock_cursor = MagicMock(), MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # fetchone calls: 1st → patient exists, 2nd → 0 linked reports
        mock_cursor.fetchone.side_effect = [
            ("Alice",),   # patient exists
            (0,),         # report count = 0
        ]

        db_tasks.delete_patient()

        delete_call = call(
            "DELETE FROM Patients WHERE patient_id = %s", (5,)
        )
        assert delete_call in mock_cursor.execute.call_args_list

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_int", return_value=5)
    def test_delete_blocked_when_reports_exist(self, mock_int, mock_get_conn, capsys):
        mock_conn, mock_cursor = MagicMock(), MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # fetchone: patient exists, then 3 linked reports
        mock_cursor.fetchone.side_effect = [
            ("Alice",),
            (3,),
        ]

        db_tasks.delete_patient()

        captured = capsys.readouterr()
        assert "Cannot delete" in captured.out
        # DELETE must NOT have been called
        for c in mock_cursor.execute.call_args_list:
            assert "DELETE" not in str(c)


# ---------------------------------------------------------------------------
# search_patients_by_name — DB layer
# ---------------------------------------------------------------------------

class TestSearchPatientsByName:

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_str", return_value="ali")
    def test_like_query_uses_wildcard(self, mock_str, mock_get_conn, capsys):
        mock_conn, mock_cursor = make_mock_conn(
            fetchall_return=[(1, "Alice", 30, "F", "9876543210")]
        )
        mock_get_conn.return_value = mock_conn

        db_tasks.search_patients_by_name()

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM Patients WHERE name LIKE %s ORDER BY name",
            ("%ali%",)
        )
        captured = capsys.readouterr()
        assert "Alice" in captured.out

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_str", return_value="zzz")
    def test_no_results_prints_not_found(self, mock_str, mock_get_conn, capsys):
        mock_conn, mock_cursor = make_mock_conn(fetchall_return=[])
        mock_get_conn.return_value = mock_conn

        db_tasks.search_patients_by_name()

        captured = capsys.readouterr()
        assert "No patients found" in captured.out


# ---------------------------------------------------------------------------
# count_tests_per_patient — DB layer
# ---------------------------------------------------------------------------

class TestCountTestsPerPatient:

    @patch("db_tasks.get_connection")
    def test_aggregate_query_contains_group_by(self, mock_get_conn, capsys):
        mock_conn, mock_cursor = make_mock_conn(
            fetchall_return=[
                (1, "Alice", "F", 3, "2024-01-10", "2024-06-15"),
                (2, "Bob",   "M", 1, "2024-03-01", "2024-03-01"),
            ]
        )
        mock_get_conn.return_value = mock_conn

        db_tasks.count_tests_per_patient()

        sql_called = mock_cursor.execute.call_args[0][0]
        assert "GROUP BY" in sql_called
        assert "COUNT" in sql_called

        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out


# ---------------------------------------------------------------------------
# add_patient_with_initial_report — atomic transaction
# ---------------------------------------------------------------------------

class TestAtomicTransaction:

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_str", side_effect=["Alice", "M", "9876543210", "Blood Test", "Normal", "yes"])
    @patch("db_tasks.get_int", side_effect=[25])
    @patch("db_tasks.get_gender", return_value="F")
    @patch("db_tasks.get_contact", return_value="9876543210")
    @patch("db_tasks.get_date", return_value="2024-06-15")
    def test_commit_calls_conn_commit(
        self, mock_date, mock_contact, mock_gender,
        mock_int, mock_str, mock_get_conn, capsys
    ):
        mock_conn, mock_cursor = MagicMock(), MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 42
        mock_get_conn.return_value = mock_conn

        # Simulate user choosing 'yes' to commit
        with patch("db_tasks.get_str", side_effect=["Alice", "Blood Test", "Normal", "yes"]):
            db_tasks.add_patient_with_initial_report()

        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_gender", return_value="M")
    @patch("db_tasks.get_contact", return_value="9876543210")
    @patch("db_tasks.get_date", return_value="2024-06-15")
    @patch("db_tasks.get_int", return_value=25)
    def test_rollback_on_user_cancel(
        self, mock_int, mock_date, mock_contact, mock_gender, mock_get_conn, capsys
    ):
        mock_conn, mock_cursor = MagicMock(), MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 42
        mock_get_conn.return_value = mock_conn

        # Simulate user choosing 'no' — both inserts should be rolled back
        with patch("db_tasks.get_str", side_effect=["Alice", "Blood Test", "Normal", "no"]):
            db_tasks.add_patient_with_initial_report()

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

        captured = capsys.readouterr()
        assert "rolled back" in captured.out.lower()

    @patch("db_tasks.get_connection")
    @patch("db_tasks.get_gender", return_value="M")
    @patch("db_tasks.get_contact", return_value="9876543210")
    @patch("db_tasks.get_date", return_value="2024-06-15")
    @patch("db_tasks.get_int", return_value=25)
    def test_two_inserts_executed_before_commit(
        self, mock_int, mock_date, mock_contact, mock_gender, mock_get_conn
    ):
        mock_conn, mock_cursor = MagicMock(), MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 10
        mock_get_conn.return_value = mock_conn

        with patch("db_tasks.get_str", side_effect=["Alice", "Blood Test", "Normal", "yes"]):
            db_tasks.add_patient_with_initial_report()

        # Verify both INSERT statements were executed
        calls_sql = [str(c) for c in mock_cursor.execute.call_args_list]
        patient_inserted = any("INSERT INTO Patients" in s for s in calls_sql)
        report_inserted  = any("INSERT INTO TestReports" in s for s in calls_sql)
        assert patient_inserted, "Patient INSERT was not executed"
        assert report_inserted,  "TestReport INSERT was not executed"
