"""Customer side: browse/filter menu, cart, place order, feedback."""
import mysql.connector

from db import get_connection, run_query
from utils import ask_int, ask_text, ask_yes_no, print_table


class Customer:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.cart = {}  # item_id -> quantity

    # ---------- menu ----------
    def get_menu(self, keyword=None, category=None, veg_only=False, max_price=None):
        sql = ("SELECT item_id, name, category, price, IF(is_veg,'Veg','Non-veg'), stock "
               "FROM menu WHERE available=1 AND stock>0")
        params = []
        if keyword:
            sql += " AND name LIKE %s"
            params.append(f"%{keyword}%")
        if category:
            sql += " AND category=%s"
            params.append(category)
        if veg_only:
            sql += " AND is_veg=1"
        if max_price is not None:
            sql += " AND price<=%s"
            params.append(max_price)
        sql += " ORDER BY category, name"
        return run_query(sql, params, fetch=True)

    def show_menu(self, **filters):
        rows = self.get_menu(**filters)
        print_table(["ID", "Item", "Category", "Price", "Type", "Left"], rows)

    def filter_menu(self):
        keyword = ask_text("Search name (Enter to skip): ", allow_blank=True) or None
        cats = [r[0] for r in run_query("SELECT DISTINCT category FROM menu WHERE available=1", fetch=True)]
        print("Categories:", ", ".join(cats))
        category = ask_text("Category (Enter to skip): ", allow_blank=True) or None
        veg_only = ask_yes_no("Veg only?")
        max_price = None
        if ask_yes_no("Set a max price?"):
            max_price = ask_int("Max price: ", lo=1)
        self.show_menu(keyword=keyword, category=category, veg_only=veg_only, max_price=max_price)

    # ---------- cart ----------
    def add_to_cart(self):
        item_id = ask_int("Item ID to add: ", lo=1)
        row = run_query("SELECT name, stock FROM menu WHERE item_id=%s AND available=1", (item_id,), fetch=True)
        if not row:
            print("No such item.")
            return
        name, stock = row[0]
        qty = ask_int(f"Quantity of {name}: ", lo=1)
        if self.cart.get(item_id, 0) + qty > stock:
            print(f"Only {stock} left in stock.")
            return
        self.cart[item_id] = self.cart.get(item_id, 0) + qty
        print(f"Added {qty} x {name}.")

    def view_cart(self, show_remove=True):
        if not self.cart:
            print("Your cart is empty.")
            return 0
        rows, total = [], 0
        for item_id, qty in self.cart.items():
            name, price = run_query("SELECT name, price FROM menu WHERE item_id=%s", (item_id,), fetch=True)[0]
            rows.append([item_id, name, qty, price, price * qty])
            total += price * qty
        print_table(["ID", "Item", "Qty", "Price", "Subtotal"], rows)
        print(f"\nTotal: {total}")
        if show_remove and ask_yes_no("Remove an item?"):
            rid = ask_int("Item ID to remove: ", lo=1)
            if self.cart.pop(rid, None) is None:
                print("That item is not in your cart.")
        return total

    # ---------- ordering ----------
    def place_order(self):
        if not self.cart:
            print("Your cart is empty.")
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            conn.start_transaction()
            lines, total = [], 0
            for item_id, qty in self.cart.items():
                cur.execute("SELECT name, price, stock FROM menu WHERE item_id=%s AND available=1 FOR UPDATE",
                            (item_id,))
                row = cur.fetchone()
                if not row or row[2] < qty:
                    raise ValueError(f"Sorry, not enough stock for item {item_id}.")
                lines.append((item_id, row[0], qty, row[1]))
                total += row[1] * qty
            cur.execute("INSERT INTO orders (user_id, total) VALUES (%s,%s)", (self.user_id, total))
            order_id = cur.lastrowid
            for item_id, _, qty, price in lines:
                cur.execute("INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                            (order_id, item_id, qty, price))
                cur.execute("UPDATE menu SET stock = stock - %s WHERE item_id=%s", (qty, item_id))
            conn.commit()
            print(f"\n===== BILL (Order #{order_id}) =====")
            print_table(["Item", "Qty", "Price", "Subtotal"], [[n, q, p, p * q] for _, n, q, p in lines])
            print(f"TOTAL: {total}\nThank you, {self.username}!")
            self.cart.clear()
        except ValueError as e:
            conn.rollback()
            print(e)
        except mysql.connector.Error as e:
            conn.rollback()
            print("Could not place order:", e)
        finally:
            cur.close()
            conn.close()

    def order_history(self):
        rows = run_query("SELECT order_id, order_time, total, status FROM orders "
                         "WHERE user_id=%s ORDER BY order_time DESC", (self.user_id,), fetch=True)
        print_table(["Order", "Time", "Total", "Status"], rows)

    # ---------- feedback ----------
    def give_feedback(self):
        kind = "complaint" if ask_yes_no("Is this a complaint? (n = general feedback)") else "feedback"
        self.order_history()
        order_id = ask_int("Order ID this is about (0 for none): ", lo=0)
        if order_id:
            owns = run_query("SELECT 1 FROM orders WHERE order_id=%s AND user_id=%s",
                             (order_id, self.user_id), fetch=True)
            if not owns:
                print("That is not one of your orders.")
                return
        rating = ask_int("Rating 1-5: ", lo=1, hi=5)
        comments = ask_text("Comments: ", allow_blank=True)
        run_query("INSERT INTO feedback (user_id, order_id, type, rating, comments) VALUES (%s,%s,%s,%s,%s)",
                  (self.user_id, order_id or None, kind, rating, comments))
        print("Thank you for your feedback!")

    # ---------- main loop ----------
    def menu_loop(self):
        actions = {
            1: lambda: self.show_menu(),
            2: self.filter_menu,
            3: self.add_to_cart,
            4: self.view_cart,
            5: self.place_order,
            6: self.order_history,
            7: self.give_feedback,
        }
        while True:
            print(f"\n--- Customer Menu ({self.username}) ---")
            print("1. Browse menu\n2. Search / filter menu\n3. Add item to cart\n4. View cart\n"
                  "5. Place order\n6. My orders\n7. Feedback / complaint\n0. Logout")
            choice = ask_int("Choice: ", lo=0, hi=7)
            if choice == 0:
                break
            actions[choice]()
