# 🏥 Pharmacy Lab Management System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange?logo=mysql)
![Tests](https://img.shields.io/badge/tests-45%20passed-brightgreen?logo=pytest)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A **CLI-based Pharmacy Laboratory Management System** built with Python and MySQL. Demonstrates real-world database design, relational queries, transaction management, input validation, logging, and a mocked test suite.

---

## ✨ Key Technical Features

| Feature | Detail |
|---|---|
| **Full CRUD** | Create, Read, Update, Delete for Patients, Reports, Labs, and Operators |
| **SQL Queries** | `LIKE` partial search, multi-table `JOIN`, `BETWEEN` date filter, `GROUP BY` + `COUNT` aggregate |
| **Atomic Transaction** | Register patient + initial report in a single atomic block — full rollback on failure |
| **Referential Integrity** | Blocks patient deletion if linked test reports exist |
| **Duplicate Prevention** | Checks for existing operator-lab assignments before inserting |
| **Indexes** | Added on `Patients.name`, `TestReports.patient_id`, `TestReports.test_date` for query performance |
| **Rotating Logger** | Activity log written to `pharmacy.log` using `RotatingFileHandler` |
| **Env-based Config** | Credentials stored in `.env` via `python-dotenv` — never hardcoded |
| **Parameterized Queries** | All SQL uses `%s` placeholders — prevents SQL injection |
| **Role-based Access** | Admin and Lab Operator roles with separate menus and permissions |
| **45 Unit Tests** | Validation tests + DB-layer tests using `unittest.mock.patch` (no real DB needed) |

---

## 📁 Project Structure

```
pharmacy-lab/
│
├── demo.py               # Entry point — database setup + role-based menus
├── db_tasks.py           # All database operations (CRUD, search, analytics, transactions)
├── config.py             # Centralized DB config loaded from .env
├── logger.py             # Shared rotating file logger
├── file.sql              # SQL schema with indexes (manual setup alternative)
│
├── .env                  # ⚠️ Credentials — DO NOT commit (see .gitignore)
├── .env.example          # Safe template to share with collaborators
├── .gitignore            # Ignores .env, __pycache__, logs, etc.
├── requirements.txt      # Pinned dependencies
│
└── tests/
    └── test_validation.py  # 45 pytest tests (validation + mocked DB layer)
```

---

## 🗄️ Database Schema

### Patients
| Column | Type | Description |
|---|---|---|
| `patient_id` | INT (PK, AUTO) | Unique patient ID |
| `name` | VARCHAR(100) | Patient name — **indexed** |
| `age` | INT | Patient age |
| `gender` | VARCHAR(10) | M / F |
| `contact` | VARCHAR(15) | Contact number |

### LabOperators
| Column | Type | Description |
|---|---|---|
| `operator_id` | INT (PK, AUTO) | Unique operator ID |
| `name` | VARCHAR(100) | Operator name |
| `contact` | VARCHAR(15) | Contact number |

### Labs
| Column | Type | Description |
|---|---|---|
| `lab_id` | INT (PK, AUTO) | Unique lab ID |
| `lab_name` | VARCHAR(100) | Lab name |
| `lab_specialization` | VARCHAR(100) | Type of tests handled |

### TestReports
| Column | Type | Description |
|---|---|---|
| `report_id` | INT (PK, AUTO) | Unique report ID |
| `patient_id` | INT (FK) | Linked patient — **indexed** |
| `test_name` | VARCHAR(100) | Name of test |
| `test_date` | DATE | Date of test — **indexed** |
| `result` | TEXT | Test result |

### LabOperatorAssignments
| Column | Type | Description |
|---|---|---|
| `assignment_id` | INT (PK, AUTO) | Unique assignment ID |
| `operator_id` | INT (FK) | Assigned operator |
| `lab_id` | INT (FK) | Assigned lab |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/pharmacy-lab-management.git
cd pharmacy-lab-management
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure credentials
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=Pharmacydb

ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
```
> ⚠️ Never commit `.env` to Git. It is already listed in `.gitignore`.

### 4. Run the application
```bash
python demo.py
```
This will automatically create the database and all required tables on first run.

---

## 🚀 Usage

On startup, select your role:

```
Welcome to the Pharmacy Lab Management System
Enter your role (1 - Lab Operator, 2 - Admin):
```

### Lab Operator Menu
```
1. Add Patient
2. Modify Patient
3. Retrieve Patient
4. Delete Patient
5. Add Report
6. Modify Report
7. Retrieve Report
8. Delete Report
9. Register Patient + Initial Report (Atomic)
A. Search & Analytics
0. Exit
```

### Search & Analytics Menu
```
1. Search Patients by Name      → partial match with LIKE
2. View All Reports for Patient → JOIN query, sorted by date
3. Filter Reports by Date Range → BETWEEN start and end date
4. Count Tests per Patient      → GROUP BY with COUNT aggregate
```

### Admin Menu
```
1. Maintain Lab Data
2. Maintain Lab Operator Data
3. Manage Operator Assignments  → assign operators to labs + view with JOIN
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
collected 45 items

tests/test_validation.py::TestAgeValidation::test_valid_age         PASSED
tests/test_validation.py::TestDeletePatient::test_delete_blocked...  PASSED
tests/test_validation.py::TestAtomicTransaction::test_rollback...    PASSED
...
45 passed in 0.21s
```

Tests are split into two layers:
- **Pure validation tests** — no DB needed, test age/gender/contact/date/string helpers
- **DB-layer tests** — use `unittest.mock.patch` to mock `mysql.connector`, validate SQL calls, commit/rollback behavior, and output messages without a real MySQL server

---

## 📝 Logging

All operations are automatically logged to `pharmacy.log` (created on first run):

```
2024-06-15 14:32:01 | INFO     | db_tasks | Patient added: name=Alice, age=28, gender=F
2024-06-15 14:32:45 | INFO     | db_tasks | Atomic transaction committed: patient_id=3, report_id=7
2024-06-15 14:33:10 | WARNING  | demo     | Failed admin login attempt for username: 'unknown'
```

Log rotates automatically after 1 MB (keeps last 3 backups).

---

## 🛠️ Technologies Used

- **Python 3.8+**
- **MySQL 8.0+**
- **mysql-connector-python** — MySQL driver
- **python-dotenv** — Environment variable management
- **pytest** — Testing framework
- **unittest.mock** — DB layer mocking (stdlib)

---

## 📚 Learning Outcomes

This project demonstrates:
- Relational database schema design with foreign keys and indexes
- Full CRUD operations with transaction control (commit / rollback)
- Multi-step atomic transactions with partial-failure rollback
- Advanced SQL: `LIKE`, `JOIN`, `BETWEEN`, `GROUP BY`, `COUNT`, `MIN`, `MAX`
- Python–MySQL integration with parameterized queries (SQL injection prevention)
- Environment-based credential management with `python-dotenv`
- Rotating file logging with `logging.handlers.RotatingFileHandler`
- Unit testing with `pytest` and DB mocking with `unittest.mock`