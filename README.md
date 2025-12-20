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

- **Backend:** Python (Flask)
- **Frontend:** HTML and CSS
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
   ```

2. Set up the MySQL database:
   - Create a new database (e.g., `clearbudget_db`)
   - Create necessary tables (see `schema.sql`)
   - Update database credentials in the Python backend

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to the web interface (`http://localhost:5000`) to begin using Clear-Budget.

---

## Usage

1. Navigate to the web interface
2. Create a new budget/project
3. Add line items:
   - Type: personnel, equipment, travel, etc.
   - Description
   - Amount / Quantity
4. Review totals, edit or delete items as needed
5. Save or export budget summary for reports or grant applications

---

## Contributing

Submit bug reports or feature requests via GitHub issues.

Pull requests are welcome for:
- Form validation enhancements
- Export options (CSV/Excel)
- Improved UI/UX
- Advanced budget categories
- User authentication

---

## License

This project is open-source under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## About

Budget builder for UofI researchers built with HTML, Python, and MySQL.

