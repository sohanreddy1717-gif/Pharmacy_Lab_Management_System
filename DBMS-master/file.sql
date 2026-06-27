-- file.sql
-- SQL schema for Pharmacy Lab Management System.
-- Includes indexes on frequently queried columns for query performance.

-- -----------------------------------------------------------------------
-- Core Tables
-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Patients (
    patient_id INT          AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    age        INT          NOT NULL,
    gender     VARCHAR(10)  NOT NULL,
    contact    VARCHAR(15)  NOT NULL
);

-- Index on name: supports LIKE-based partial name searches efficiently
CREATE INDEX IF NOT EXISTS idx_patients_name ON Patients(name);

-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS LabOperators (
    operator_id INT          AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    contact     VARCHAR(15)  NOT NULL
);

-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Labs (
    lab_id             INT          AUTO_INCREMENT PRIMARY KEY,
    lab_name           VARCHAR(100) NOT NULL,
    lab_specialization VARCHAR(100) NOT NULL
);

-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS TestReports (
    report_id  INT          AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    test_name  VARCHAR(100) NOT NULL,
    test_date  DATE         NOT NULL,
    result     TEXT         NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Index on patient_id: supports "all reports for a patient" JOIN queries
CREATE INDEX IF NOT EXISTS idx_testreports_patient_id ON TestReports(patient_id);

-- Index on test_date: supports date-range filter queries efficiently
CREATE INDEX IF NOT EXISTS idx_testreports_test_date  ON TestReports(test_date);

-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS LabOperatorAssignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    operator_id   INT,
    lab_id        INT,
    FOREIGN KEY (operator_id) REFERENCES LabOperators(operator_id),
    FOREIGN KEY (lab_id)      REFERENCES Labs(lab_id)
);
