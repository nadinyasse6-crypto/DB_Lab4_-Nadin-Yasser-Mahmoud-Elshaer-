# Library Management System - Lab Project

## Student Information
* **Name:** Nadin Yasser | **ID:** 2304091
* **Name:** Mahmoud Elshaer | **ID:** 2304092
* **Course:** Introduction to Database Systems - Lab Work
* **University:** Alexandria National University, Faculty of Engineering

## Project Overview
A web-based Library Management System built using Python (Flask), MySQL, and Bootstrap as part of the Database Systems Lab coursework. It features user authentication with automatic member registration, full CRUD operations, advanced database queries, reports, book loans management, manual text-based categories and publishers, and relational constraints with cascading deletes (`ON DELETE CASCADE`).

## Project Structure
```text
my-library-project/
│
├── app.py
├── schema.sql
└── templates/
    ├── login.html
    ├── register.html
    ├── index.html
    ├── authors.html
    ├── catalogue.html
    ├── edit_author.html
    ├── edit_book.html
    ├── loans.html
    ├── add_loan.html
    ├── reports.html
    ├── search_books.html
    ├── most_borrowed.html
    └── authors_books.html
```

## Prerequisites
Ensure you have the following installed on your system:
* Python 3
* MySQL Server / MySQL Workbench
* Required Python Libraries (`Flask`, `Flask-Bcrypt`, `PyMySQL`)

## How to Run Step by Step

### Step 1: Database Setup
1. Open **MySQL Workbench**.
2. Run your database schema script (`schema.sql`) to create the database (`library_db`) and tables (`users`, `AUTHOR`, `PUBLISHER`, `CATEGORY`, `BOOK`, `MEMBER`, `LOAN`) with all foreign key constraints and cascading rules.

### Step 2: Install Dependencies
Open your terminal in the project directory and run:
```bash
pip install Flask flask-bcrypt PyMySQL
```

### Step 3: Configure Database Connection
Open `app.py` and verify your MySQL connection settings (username and password):
```python
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='YOUR_PASSWORD',
        database='library_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
```

### Step 4: Run the Application
Execute the following command in your terminal:
```bash
python app.py
```

### Step 5: Access the Website
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```
Register a new account (which automatically registers you as a member), manage authors, books, text-based categories, and publishers, and explore the lab features including search, reports, and loans management!
