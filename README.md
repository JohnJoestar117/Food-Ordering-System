# Automated Food Ordering, Feedback, and Management System

A desktop (console) restaurant system built with **Python 3**, **MySQL** and **mysql.connector**.
Customers browse/filter the menu, place orders and leave feedback; administrators manage the menu,
stock, orders, complaints and sales reports.

## Features
**Customer:** register/login, browse menu, search and filter (name, category, veg/non-veg, max price),
cart, bill generation, order history, feedback and complaints.

**Admin:** add/update menu items, stock control and low-stock alerts, view and update orders,
review and resolve complaints, sales reports (revenue, daily totals, top items, average rating).

## Setup
1.Clone the repo, then `cd food-ordering-system`(the folder path) before running any commands.
2. Install Python 3 and MySQL Server.
3. `pip install -r requirements.txt`
4. Copy `config.example.py` to `config.py` and enter your MySQL password.
5. `python setup_db.py` (creates the database, tables, sample menu and a default admin).
6. `python main.py`

Default admin: `admin` / `admin123` (change after first login).

## Project structure
| File | Purpose |
|------|---------|
| `main.py` | Entry point, login/register, role routing |
| `db.py` | MySQL connection and query helper |
| `auth.py` | Password hashing, login, registration |
| `customer.py` | `Customer` class (customer features) |
| `admin.py` | `Admin` class (admin features) |
| `utils.py` | Input validation and table printing |
| `schema.sql` | Database schema and sample data |
| `setup_db.py` | One-time database setup |
| `docs/` | Abstract, report, ER diagram |
| `screenshots/` | Output screenshots for the report |

## Team
Group 9: Jonathan, Naail, Jerfin.
