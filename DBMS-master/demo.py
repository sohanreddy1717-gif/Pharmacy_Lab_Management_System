"""
demo.py
-------
Entry point for the Pharmacy Lab Management System.
Sets up the database, creates tables, and routes users to their role-based menu.
"""

import mysql.connector
from mysql.connector import Error

import db_tasks
from config import DB_CONFIG_NO_DB, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD
from logger import logger


# ---------------------------------------------------------------------------
# Database Setup
# ---------------------------------------------------------------------------

def create_database():
    """Create the Pharmacydb database if it does not already exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG_NO_DB)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        logger.info(f"Database '{DB_NAME}' is ready.")
        print(f"Database '{DB_NAME}' is ready.")
    except Error as e:
        logger.error(f"Failed to create database: {e}")
        print(e)
    finally:
        cursor.close()
        conn.close()


def create_tables():
    """Create all required tables if they do not already exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG_NO_DB, database=DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patients (
                patient_id INT AUTO_INCREMENT PRIMARY KEY,
                name       VARCHAR(100) NOT NULL,
                age        INT          NOT NULL,
                gender     VARCHAR(10)  NOT NULL,
                contact    VARCHAR(15)  NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LabOperators (
                operator_id INT AUTO_INCREMENT PRIMARY KEY,
                name        VARCHAR(100) NOT NULL,
                contact     VARCHAR(15)  NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Labs (
                lab_id             INT AUTO_INCREMENT PRIMARY KEY,
                lab_name           VARCHAR(100) NOT NULL,
                lab_specialization VARCHAR(100) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TestReports (
                report_id  INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                test_name  VARCHAR(100) NOT NULL,
                test_date  DATE         NOT NULL,
                result     TEXT         NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LabOperatorAssignments (
                assignment_id INT AUTO_INCREMENT PRIMARY KEY,
                operator_id   INT,
                lab_id        INT,
                FOREIGN KEY (operator_id) REFERENCES LabOperators(operator_id),
                FOREIGN KEY (lab_id)      REFERENCES Labs(lab_id)
            )
        """)

        logger.info("All required tables are ready.")
        print("All required tables are ready.")
    except Error as e:
        logger.error(f"Failed to create tables: {e}")
        print(e)
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def authenticate_admin():
    """Verify admin credentials against environment-configured values."""
    username = input("Enter Admin Username: ")
    password = input("Enter Admin Password: ")
    authenticated = (username == ADMIN_USERNAME and password == ADMIN_PASSWORD)
    if not authenticated:
        logger.warning(f"Failed admin login attempt for username: '{username}'")
    else:
        logger.info(f"Admin '{username}' logged in successfully.")
    return authenticated


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

def lab_operator_menu():
    """Menu for Lab Operator role — full CRUD on Patients and Reports."""
    while True:
        print("\n--- Lab Operator Menu ---")
        print("1. Add Patient")
        print("2. Modify Patient")
        print("3. Retrieve Patient")
        print("4. Delete Patient")
        print("5. Add Report")
        print("6. Modify Report")
        print("7. Retrieve Report")
        print("8. Delete Report")
        print("9. Register Patient + Initial Report (Atomic)")
        print("A. Search & Analytics")
        print("0. Exit to Main Menu")

        choice_input = input("Enter your choice: ").strip().upper()

        if choice_input == "1":
            db_tasks.add_patient()
        elif choice_input == "2":
            db_tasks.modify_patient()
        elif choice_input == "3":
            db_tasks.retrieve_patient()
        elif choice_input == "4":
            db_tasks.delete_patient()
        elif choice_input == "5":
            db_tasks.add_report()
        elif choice_input == "6":
            db_tasks.modify_report()
        elif choice_input == "7":
            db_tasks.retrieve_report()
        elif choice_input == "8":
            db_tasks.delete_report()
        elif choice_input == "9":
            db_tasks.add_patient_with_initial_report()
        elif choice_input == "A":
            analytics_menu()
        elif choice_input == "0":
            print("Returning to Main Menu...")
            return
        else:
            print("❌ Invalid choice. Try again.")


def analytics_menu():
    """Sub-menu for search, filter, and analytics queries."""
    while True:
        print("\n--- Search & Analytics ---")
        print("1. Search Patients by Name (partial match)")
        print("2. View All Reports for a Patient (JOIN)")
        print("3. Filter Reports by Date Range")
        print("4. Count Tests per Patient (GROUP BY / Aggregate)")
        print("0. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            db_tasks.search_patients_by_name()
        elif choice == "2":
            db_tasks.get_all_reports_for_patient()
        elif choice == "3":
            db_tasks.filter_reports_by_date_range()
        elif choice == "4":
            db_tasks.count_tests_per_patient()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")


def admin_menu():
    """Menu for Admin role — manage Labs, Operators, and Assignments."""
    while True:
        print("\n--- Admin Menu ---")
        print("1. Maintain Lab Data")
        print("2. Maintain Lab Operator Data")
        print("3. Manage Operator Assignments")
        print("0. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            db_tasks.maintain_lab_data()
        elif choice == "2":
            db_tasks.maintain_lab_operator_data()
        elif choice == "3":
            assignments_menu()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")


def assignments_menu():
    """Sub-menu for managing Lab Operator Assignments."""
    while True:
        print("\n--- Operator Assignments ---")
        print("1. Assign Operator to Lab")
        print("2. View All Assignments")
        print("0. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            db_tasks.assign_operator_to_lab()
        elif choice == "2":
            db_tasks.view_operator_assignments()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    create_database()
    create_tables()

    print("\nWelcome to the Pharmacy Lab Management System")
    role = input("Enter your role (1 - Lab Operator, 2 - Admin): ")

    if role == "1":
        lab_operator_menu()
    elif role == "2":
        if authenticate_admin():
            admin_menu()
        else:
            print("❌ Authentication failed. Access denied.")
    else:
        print("❌ Invalid role selected.")


if __name__ == "__main__":
    main()