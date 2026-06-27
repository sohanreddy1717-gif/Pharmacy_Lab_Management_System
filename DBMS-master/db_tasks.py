"""
db_tasks.py
-----------
Database operation functions for the Pharmacy Lab Management System.
Handles all CRUD operations for Patients, TestReports, Labs,
LabOperators, and LabOperatorAssignments.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

from config import DB_CONFIG
from logger import logger


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection():
    """Return a new MySQL connection using centralized config."""
    return mysql.connector.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# Input Helpers
# ---------------------------------------------------------------------------

def get_int(prompt):
    """Prompt the user until a valid integer is entered."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("❌ Please enter a valid number.")


def get_str(prompt):
    """Prompt the user until a non-empty string is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("❌ This field cannot be empty.")


def get_date(prompt):
    """Prompt the user until a valid YYYY-MM-DD date string is entered."""
    while True:
        date_str = input(prompt).strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("❌ Invalid date. Please use the format YYYY-MM-DD (e.g. 2024-06-15).")


def get_gender(prompt="Enter gender (M/F): "):
    """Prompt the user until M or F is entered."""
    while True:
        gender = get_str(prompt).upper()
        if gender in ('M', 'F'):
            return gender
        print("❌ Invalid gender. Please enter 'M' for Male or 'F' for Female.")


def get_contact(prompt="Enter contact number: "):
    """Prompt the user until a valid 7–15 digit contact number is entered."""
    while True:
        contact = get_str(prompt)
        if contact.isdigit() and 7 <= len(contact) <= 15:
            return contact
        print("❌ Invalid contact. Enter digits only (7–15 characters).")


def confirm_commit(conn):
    """Ask user to commit or rollback a pending transaction. Returns True if committed."""
    choice = get_str("Do you want to commit the changes? (yes/no): ").lower()
    if choice == 'yes':
        conn.commit()
        return True
    conn.rollback()
    print("❌ Changes rolled back.")
    return False


# ---------------------------------------------------------------------------
# Patient Functions
# ---------------------------------------------------------------------------

def add_patient():
    """Insert a new patient record with user confirmation."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        name = get_str("Enter name: ")

        while True:
            age = get_int("Enter age: ")
            if age > 0:
                break
            print("❌ Please enter a valid age (positive integer).")

        gender = get_gender()
        contact = get_contact()

        cursor.execute(
            "INSERT INTO Patients (name, age, gender, contact) VALUES (%s, %s, %s, %s)",
            (name, age, gender, contact)
        )

        if confirm_commit(conn):
            logger.info(f"Patient added: name={name}, age={age}, gender={gender}")
            print("✅ Patient added successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error adding patient: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def modify_patient():
    """Update an existing patient record by ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        patient_id = get_int("Enter Patient ID to modify: ")

        # Check if patient exists first
        cursor.execute("SELECT patient_id FROM Patients WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            print("❌ No patient found with that ID.")
            return

        name = get_str("Enter new name: ")

        while True:
            age = get_int("Enter new age: ")
            if age > 0:
                break
            print("❌ Please enter a valid age (positive integer).")

        gender = get_gender()
        contact = get_contact()

        cursor.execute(
            "UPDATE Patients SET name=%s, age=%s, gender=%s, contact=%s WHERE patient_id=%s",
            (name, age, gender, contact, patient_id)
        )

        if confirm_commit(conn):
            logger.info(f"Patient modified: patient_id={patient_id}")
            print("✅ Patient updated successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error modifying patient: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def retrieve_patient():
    """Fetch and display a single patient record by ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        patient_id = get_int("Enter Patient ID to retrieve: ")
        cursor.execute("SELECT * FROM Patients WHERE patient_id = %s", (patient_id,))
        record = cursor.fetchone()

        if record:
            print("\n--- Patient Details ---")
            print(f"ID      : {record[0]}")
            print(f"Name    : {record[1]}")
            print(f"Age     : {record[2]}")
            print(f"Gender  : {record[3]}")
            print(f"Contact : {record[4]}")
            logger.info(f"Patient retrieved: patient_id={patient_id}")
        else:
            print("❌ No patient found with that ID.")

    except Error as e:
        logger.error(f"Error retrieving patient: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def delete_patient():
    """
    Delete a patient by ID.
    Blocked if the patient has linked test reports (referential integrity).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        patient_id = get_int("Enter Patient ID to delete: ")

        # Check existence
        cursor.execute("SELECT name FROM Patients WHERE patient_id = %s", (patient_id,))
        row = cursor.fetchone()
        if not row:
            print("❌ No patient found with that ID.")
            return

        # Check for linked reports
        cursor.execute(
            "SELECT COUNT(*) FROM TestReports WHERE patient_id = %s", (patient_id,)
        )
        report_count = cursor.fetchone()[0]
        if report_count > 0:
            print(
                f"❌ Cannot delete: Patient '{row[0]}' has {report_count} linked test report(s).\n"
                "   Please delete those reports first."
            )
            return

        print(f"⚠️  You are about to delete patient: '{row[0]}' (ID: {patient_id})")
        cursor.execute("DELETE FROM Patients WHERE patient_id = %s", (patient_id,))

        if confirm_commit(conn):
            logger.info(f"Patient deleted: patient_id={patient_id}, name={row[0]}")
            print("✅ Patient deleted successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error deleting patient: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Test Report Functions
# ---------------------------------------------------------------------------

def add_report():
    """Insert a new test report for an existing patient."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        patient_id = get_int("Enter Patient ID: ")

        # Verify patient exists
        cursor.execute("SELECT patient_id FROM Patients WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            print("❌ No patient found with that ID. Please add the patient first.")
            return

        test_name = get_str("Enter test name: ")
        test_date = get_date("Enter test date (YYYY-MM-DD): ")
        result = get_str("Enter test result: ")

        cursor.execute(
            "INSERT INTO TestReports (patient_id, test_name, test_date, result) "
            "VALUES (%s, %s, %s, %s)",
            (patient_id, test_name, test_date, result)
        )

        if confirm_commit(conn):
            logger.info(f"Report added: patient_id={patient_id}, test={test_name}, date={test_date}")
            print("✅ Report added successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error adding report: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def modify_report():
    """Update an existing test report by report ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        report_id = get_int("Enter Report ID to modify: ")

        # Check existence
        cursor.execute("SELECT report_id FROM TestReports WHERE report_id = %s", (report_id,))
        if not cursor.fetchone():
            print("❌ No report found with that ID.")
            return

        patient_id = get_int("Enter new Patient ID: ")
        test_name = get_str("Enter new test name: ")
        test_date = get_date("Enter new test date (YYYY-MM-DD): ")
        result = get_str("Enter new test result: ")

        cursor.execute(
            "UPDATE TestReports SET patient_id=%s, test_name=%s, test_date=%s, result=%s "
            "WHERE report_id=%s",
            (patient_id, test_name, test_date, result, report_id)
        )

        if confirm_commit(conn):
            logger.info(f"Report modified: report_id={report_id}")
            print("✅ Report updated successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error modifying report: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def retrieve_report():
    """Fetch and display a single test report by ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        report_id = get_int("Enter Report ID to retrieve: ")
        cursor.execute("SELECT * FROM TestReports WHERE report_id = %s", (report_id,))
        record = cursor.fetchone()

        if record:
            print("\n--- Test Report Details ---")
            print(f"Report ID   : {record[0]}")
            print(f"Patient ID  : {record[1]}")
            print(f"Test Name   : {record[2]}")
            print(f"Test Date   : {record[3]}")
            print(f"Result      : {record[4]}")
            logger.info(f"Report retrieved: report_id={report_id}")
        else:
            print("❌ No report found with that ID.")

    except Error as e:
        logger.error(f"Error retrieving report: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def delete_report():
    """Delete a test report by ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        report_id = get_int("Enter Report ID to delete: ")

        cursor.execute(
            "SELECT test_name, patient_id FROM TestReports WHERE report_id = %s", (report_id,)
        )
        row = cursor.fetchone()
        if not row:
            print("❌ No report found with that ID.")
            return

        print(f"⚠️  You are about to delete report: '{row[0]}' for Patient ID {row[1]}")
        cursor.execute("DELETE FROM TestReports WHERE report_id = %s", (report_id,))

        if confirm_commit(conn):
            logger.info(f"Report deleted: report_id={report_id}")
            print("✅ Report deleted successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error deleting report: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Admin — Lab Functions
# ---------------------------------------------------------------------------

def maintain_lab_data():
    """Admin sub-menu to add, update, or view labs."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        while True:
            print("\n--- Maintain Lab Data ---")
            print("1. Add Lab")
            print("2. Update Lab")
            print("3. View All Labs")
            print("0. Back")
            choice = get_str("Enter your choice: ")

            if choice == "1":
                lab_name = get_str("Enter lab name: ")
                specialization = get_str("Enter specialization: ")
                cursor.execute(
                    "INSERT INTO Labs (lab_name, lab_specialization) VALUES (%s, %s)",
                    (lab_name, specialization)
                )
                if confirm_commit(conn):
                    logger.info(f"Lab added: name={lab_name}, specialization={specialization}")
                    print("✅ Lab added successfully.")

            elif choice == "2":
                lab_id = get_int("Enter Lab ID to update: ")
                lab_name = get_str("Enter new lab name: ")
                specialization = get_str("Enter new specialization: ")
                cursor.execute(
                    "UPDATE Labs SET lab_name=%s, lab_specialization=%s WHERE lab_id=%s",
                    (lab_name, specialization, lab_id)
                )
                if confirm_commit(conn):
                    if cursor.rowcount:
                        logger.info(f"Lab updated: lab_id={lab_id}")
                        print("✅ Lab updated successfully.")
                    else:
                        print("❌ Lab not found.")

            elif choice == "3":
                cursor.execute("SELECT * FROM Labs")
                rows = cursor.fetchall()
                if rows:
                    print("\n{:<10} {:<25} {}".format("Lab ID", "Name", "Specialization"))
                    print("-" * 55)
                    for row in rows:
                        print("{:<10} {:<25} {}".format(row[0], row[1], row[2]))
                else:
                    print("No labs found.")

            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error in lab data management: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Admin — Lab Operator Functions
# ---------------------------------------------------------------------------

def maintain_lab_operator_data():
    """Admin sub-menu to add, update, or view lab operators."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        while True:
            print("\n--- Maintain Lab Operator Data ---")
            print("1. Add Lab Operator")
            print("2. Update Lab Operator")
            print("3. View All Lab Operators")
            print("0. Back")
            choice = get_str("Enter your choice: ")

            if choice == "1":
                name = get_str("Enter operator name: ")
                contact = get_contact("Enter operator contact: ")
                cursor.execute(
                    "INSERT INTO LabOperators (name, contact) VALUES (%s, %s)",
                    (name, contact)
                )
                if confirm_commit(conn):
                    logger.info(f"Lab operator added: name={name}")
                    print("✅ Lab operator added successfully.")

            elif choice == "2":
                operator_id = get_int("Enter Operator ID to update: ")
                name = get_str("Enter new operator name: ")
                contact = get_contact("Enter new contact: ")
                cursor.execute(
                    "UPDATE LabOperators SET name=%s, contact=%s WHERE operator_id=%s",
                    (name, contact, operator_id)
                )
                if confirm_commit(conn):
                    if cursor.rowcount:
                        logger.info(f"Lab operator updated: operator_id={operator_id}")
                        print("✅ Lab operator updated successfully.")
                    else:
                        print("❌ Operator not found.")

            elif choice == "3":
                cursor.execute("SELECT * FROM LabOperators")
                rows = cursor.fetchall()
                if rows:
                    print("\n{:<12} {:<25} {}".format("Operator ID", "Name", "Contact"))
                    print("-" * 50)
                    for row in rows:
                        print("{:<12} {:<25} {}".format(row[0], row[1], row[2]))
                else:
                    print("No lab operators found.")

            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error in lab operator management: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Admin — Lab Operator Assignments (previously unused table — now implemented)
# ---------------------------------------------------------------------------

def assign_operator_to_lab():
    """Assign an existing lab operator to an existing lab."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        operator_id = get_int("Enter Operator ID to assign: ")
        cursor.execute("SELECT name FROM LabOperators WHERE operator_id=%s", (operator_id,))
        op_row = cursor.fetchone()
        if not op_row:
            print("❌ No operator found with that ID.")
            return

        lab_id = get_int("Enter Lab ID to assign operator to: ")
        cursor.execute("SELECT lab_name FROM Labs WHERE lab_id=%s", (lab_id,))
        lab_row = cursor.fetchone()
        if not lab_row:
            print("❌ No lab found with that ID.")
            return

        # Check for duplicate assignment
        cursor.execute(
            "SELECT assignment_id FROM LabOperatorAssignments "
            "WHERE operator_id=%s AND lab_id=%s",
            (operator_id, lab_id)
        )
        if cursor.fetchone():
            print(
                f"⚠️  Operator '{op_row[0]}' is already assigned to lab '{lab_row[0]}'."
            )
            return

        cursor.execute(
            "INSERT INTO LabOperatorAssignments (operator_id, lab_id) VALUES (%s, %s)",
            (operator_id, lab_id)
        )

        if confirm_commit(conn):
            logger.info(
                f"Assignment created: operator_id={operator_id}, lab_id={lab_id}"
            )
            print(f"✅ Operator '{op_row[0]}' assigned to lab '{lab_row[0]}' successfully.")

    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error assigning operator to lab: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def view_operator_assignments():
    """Display all operator-lab assignments with names (JOIN query)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                loa.assignment_id,
                lo.name  AS operator_name,
                lo.contact AS operator_contact,
                l.lab_name,
                l.lab_specialization
            FROM LabOperatorAssignments loa
            JOIN LabOperators lo ON loa.operator_id = lo.operator_id
            JOIN Labs         l  ON loa.lab_id      = l.lab_id
            ORDER BY loa.assignment_id
        """)
        rows = cursor.fetchall()

        if rows:
            print("\n{:<6} {:<20} {:<15} {:<20} {}".format(
                "Asn ID", "Operator", "Contact", "Lab", "Specialization"
            ))
            print("-" * 80)
            for row in rows:
                print("{:<6} {:<20} {:<15} {:<20} {}".format(*row))
            logger.info("Viewed all operator assignments.")
        else:
            print("No assignments found.")

    except Error as e:
        logger.error(f"Error viewing assignments: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Search & Filter Queries
# ---------------------------------------------------------------------------

def search_patients_by_name():
    """
    Search patients using a partial name match (SQL LIKE).
    Demonstrates: WHERE clause with LIKE for partial text search.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        keyword = get_str("Enter name or partial name to search: ")

        cursor.execute(
            "SELECT * FROM Patients WHERE name LIKE %s ORDER BY name",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()

        if rows:
            print(f"\n{len(rows)} patient(s) found matching '{keyword}':")
            print("{:<10} {:<25} {:<5} {:<8} {}".format(
                "ID", "Name", "Age", "Gender", "Contact"
            ))
            print("-" * 60)
            for row in rows:
                print("{:<10} {:<25} {:<5} {:<8} {}".format(*row))
            logger.info(f"Patient search: keyword='{keyword}', results={len(rows)}")
        else:
            print(f"❌ No patients found matching '{keyword}'.")

    except Error as e:
        logger.error(f"Error searching patients: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def get_all_reports_for_patient():
    """
    Retrieve all test reports for a given patient using a JOIN query.
    Demonstrates: multi-table JOIN, filtering by foreign key.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        patient_id = get_int("Enter Patient ID: ")

        cursor.execute(
            "SELECT p.name, p.age, p.gender FROM Patients p WHERE p.patient_id = %s",
            (patient_id,)
        )
        patient = cursor.fetchone()
        if not patient:
            print("❌ No patient found with that ID.")
            return

        cursor.execute("""
            SELECT
                tr.report_id,
                tr.test_name,
                tr.test_date,
                tr.result
            FROM TestReports tr
            JOIN Patients    p  ON tr.patient_id = p.patient_id
            WHERE tr.patient_id = %s
            ORDER BY tr.test_date DESC
        """, (patient_id,))
        rows = cursor.fetchall()

        print(f"\nPatient: {patient[0]} | Age: {patient[1]} | Gender: {patient[2]}")
        if rows:
            print(f"\n{len(rows)} report(s) found:")
            print("{:<10} {:<25} {:<12} {}".format(
                "Report ID", "Test Name", "Date", "Result"
            ))
            print("-" * 70)
            for row in rows:
                print("{:<10} {:<25} {:<12} {}".format(*row))
            logger.info(f"Reports fetched for patient_id={patient_id}, count={len(rows)}")
        else:
            print("No test reports found for this patient.")

    except Error as e:
        logger.error(f"Error fetching reports for patient: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def filter_reports_by_date_range():
    """
    Retrieve test reports within a user-specified date range.
    Demonstrates: WHERE with BETWEEN on a DATE column, indexed query.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("Filter test reports by date range.")
        start_date = get_date("Enter start date (YYYY-MM-DD): ")
        end_date   = get_date("Enter end date   (YYYY-MM-DD): ")

        if end_date < start_date:
            print("❌ End date cannot be before start date.")
            return

        cursor.execute("""
            SELECT
                tr.report_id,
                p.name        AS patient_name,
                tr.test_name,
                tr.test_date,
                tr.result
            FROM TestReports tr
            JOIN Patients    p ON tr.patient_id = p.patient_id
            WHERE tr.test_date BETWEEN %s AND %s
            ORDER BY tr.test_date ASC
        """, (start_date, end_date))
        rows = cursor.fetchall()

        if rows:
            print(f"\n{len(rows)} report(s) between {start_date} and {end_date}:")
            print("{:<10} {:<20} {:<25} {:<12} {}".format(
                "Report ID", "Patient", "Test Name", "Date", "Result"
            ))
            print("-" * 85)
            for row in rows:
                print("{:<10} {:<20} {:<25} {:<12} {}".format(*row))
            logger.info(
                f"Date-range filter: {start_date} to {end_date}, results={len(rows)}"
            )
        else:
            print(f"No reports found between {start_date} and {end_date}.")

    except Error as e:
        logger.error(f"Error filtering reports by date: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def count_tests_per_patient():
    """
    Display the total number of tests conducted per patient.
    Demonstrates: GROUP BY with COUNT aggregate, ORDER BY, JOIN.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.patient_id,
                p.name,
                p.gender,
                COUNT(tr.report_id)  AS total_tests,
                MIN(tr.test_date)    AS first_test,
                MAX(tr.test_date)    AS latest_test
            FROM Patients    p
            LEFT JOIN TestReports tr ON p.patient_id = tr.patient_id
            GROUP BY p.patient_id, p.name, p.gender
            ORDER BY total_tests DESC
        """)
        rows = cursor.fetchall()

        if rows:
            print("\n--- Test Count per Patient ---")
            print("{:<10} {:<25} {:<8} {:<12} {:<12} {}".format(
                "ID", "Name", "Gender", "Total Tests", "First Test", "Latest Test"
            ))
            print("-" * 80)
            for row in rows:
                print("{:<10} {:<25} {:<8} {:<12} {:<12} {}".format(
                    row[0], row[1], row[2], row[3],
                    str(row[4]) if row[4] else "N/A",
                    str(row[5]) if row[5] else "N/A"
                ))
            logger.info("Test-count-per-patient report generated.")
        else:
            print("No patients found.")

    except Error as e:
        logger.error(f"Error counting tests per patient: {e}")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Atomic Multi-Step Transaction
# ---------------------------------------------------------------------------

def add_patient_with_initial_report():
    """
    Atomically register a new patient AND create their first test report
    in a single transaction. If the report insert fails for any reason,
    the patient insert is also rolled back — leaving the DB in a clean state.

    Demonstrates: real multi-step atomic transaction with partial-failure rollback.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        # Disable autocommit — we manage the transaction manually
        conn.autocommit = False
        cursor = conn.cursor()

        print("\n--- Register New Patient with Initial Test Report ---")

        # ---- Step 1: Collect patient details ----
        print("\n[Step 1 of 2] Patient Details")
        name = get_str("Enter patient name: ")

        while True:
            age = get_int("Enter patient age: ")
            if age > 0:
                break
            print("❌ Please enter a valid age (positive integer).")

        gender  = get_gender()
        contact = get_contact()

        # ---- Step 2: Collect report details ----
        print("\n[Step 2 of 2] Initial Test Report")
        test_name = get_str("Enter test name: ")
        test_date = get_date("Enter test date (YYYY-MM-DD): ")
        result    = get_str("Enter test result: ")

        # ---- Execute Step 1: Insert patient ----
        cursor.execute(
            "INSERT INTO Patients (name, age, gender, contact) VALUES (%s, %s, %s, %s)",
            (name, age, gender, contact)
        )
        new_patient_id = cursor.lastrowid
        logger.debug(f"[Transaction] Patient row inserted: temp_id={new_patient_id}")

        # ---- Execute Step 2: Insert report (linked to new patient) ----
        cursor.execute(
            "INSERT INTO TestReports (patient_id, test_name, test_date, result) "
            "VALUES (%s, %s, %s, %s)",
            (new_patient_id, test_name, test_date, result)
        )
        new_report_id = cursor.lastrowid
        logger.debug(f"[Transaction] Report row inserted: temp_id={new_report_id}")

        # ---- Confirm and commit BOTH together ----
        print(f"\n  Patient : {name} | Age: {age} | {gender} | {contact}")
        print(f"  Report  : {test_name} on {test_date} — Result: {result}")

        choice = get_str("\nCommit both patient and report? (yes/no): ").lower()
        if choice == 'yes':
            conn.commit()
            logger.info(
                f"Atomic transaction committed: patient_id={new_patient_id}, "
                f"report_id={new_report_id}, name={name}"
            )
            print(f"✅ Patient (ID: {new_patient_id}) and Report (ID: {new_report_id}) "
                  f"saved successfully.")
        else:
            conn.rollback()
            # Both inserts are undone — DB is clean
            logger.info("Atomic transaction rolled back by user.")
            print("❌ Both patient and report rolled back. No changes saved.")

    except Error as e:
        # Partial failure: roll back everything so DB stays consistent
        if conn:
            conn.rollback()
            logger.error(
                f"Atomic transaction rolled back due to error: {e}"
            )
        print(f"❌ Transaction failed and was fully rolled back.\nError: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.autocommit = True  # Restore default behaviour
            conn.close()
