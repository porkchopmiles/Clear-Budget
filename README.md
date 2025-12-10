# Clear-Budget

[![Python](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Clear-Budget** is a lightweight budget builder application designed for researchers and departments. It allows creating, managing, and exporting project budgets easily.

---

## Features

- Create project budgets with line items (personnel, equipment, travel, overhead, etc.)  
- Store and manage multiple project budgets in a MySQL database  
- Simple web interface for entering and reviewing budget items  
- Export or view your budget summary for grant proposals or internal planning

---

## Tech Stack

- **Backend:** Python (Flask or similar)  
- **Frontend:** HTML (optionally with CSS/JS enhancements)  
- **Database:** MySQL  
- Lightweight and easy to deploy locally or on a server

---

## Getting Started

### Prerequisites

- Python 3.x  
- MySQL or MariaDB  
- A web server or local environment for Python + HTML  
- Basic familiarity with SQL and Python configuration

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/porkchopmiles/Clear-Budget.git
   cd Clear-Budget
Set up the MySQL database:

Create a new database (e.g., clearbudget_db)

Create necessary tables (see schema.sql if available)

Update database credentials in the Python backend

Install Python dependencies (if provided):

bash
Copy code
pip install -r requirements.txt
Start the backend server:

bash
Copy code
python app.py
Open your browser and navigate to the web interface (usually http://localhost:5000) to begin using Clear-Budget.

Usage
Navigate to the web interface

Create a new budget/project

Add line items:

Type: personnel, equipment, travel, etc.

Description

Amount / Quantity

Review totals, edit or delete items as needed

Save or export budget summary for reports or grant applications

Example Database Schema
sql
Copy code
CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE budget_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    budget_id INT,
    category VARCHAR(100),
    description VARCHAR(255),
    amount DECIMAL(10,2),
    quantity INT,
    FOREIGN KEY (budget_id) REFERENCES budgets(id)
);
Contributing
Submit bug reports or feature requests via GitHub issues

Pull requests are welcome for:

Form validation enhancements

Export options (CSV/Excel)

Improved UI/UX

Advanced budget categories

User authentication

License
This project is open-source under the MIT License. See the LICENSE file for details.