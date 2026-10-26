import mysql.connector

import auth
from admin import Admin
from customer import Customer
from utils import ask_int, ask_text


def main():
    print("=== Automated Food Ordering, Feedback & Management System ===")
    while True:
        print("\n1. Login\n2. Register (customer)\n0. Exit")
        choice = ask_int("Choice: ", lo=0, hi=2)
        if choice == 0:
            print("Goodbye!")
            break
        username = ask_text("Username: ")
        password = ask_text("Password: ")
        if choice == 2:
            if auth.register(username, password):
                print("Account created. You can log in now.")
            else:
                print("That username is taken.")
            continue
        result = auth.login(username, password)
        if not result:
            print("Invalid username or password.")
            continue
        user_id, role = result
        (Admin if role == "admin" else Customer)(user_id, username).menu_loop()


if __name__ == "__main__":
    try:
        main()
    except mysql.connector.Error as e:
        print("Database error:", e)
        print("Check config.py and make sure MySQL is running and setup_db.py has been run.")
    except KeyboardInterrupt:
        print("\nGoodbye!")
