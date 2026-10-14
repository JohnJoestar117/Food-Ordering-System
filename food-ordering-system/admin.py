"""Admin side: manage menu/stock, orders, feedback, sales reports."""
from db import run_query
from utils import ask_float, ask_int, ask_text, ask_yes_no, print_table


class Admin:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    # ---------- menu & inventory ----------
    def view_menu(self):
        rows = run_query("SELECT item_id, name, category, price, IF(is_veg,'Veg','Non-veg'), stock, "
                         "IF(available,'Yes','No') FROM menu ORDER BY category, name", fetch=True)
        print_table(["ID", "Item", "Category", "Price", "Type", "Stock", "Listed"], rows)

    def add_item(self):
        name = ask_text("Item name: ")
        category = ask_text("Category: ")
        price = ask_float("Price: ")
        is_veg = ask_yes_no("Vegetarian?")
        stock = ask_int("Starting stock: ", lo=0)
        run_query("INSERT INTO menu (name, category, price, is_veg, stock) VALUES (%s,%s,%s,%s,%s)",
                  (name, category, price, is_veg, stock))
        print("Item added.")

    def update_item(self):
        self.view_menu()
        item_id = ask_int("Item ID to update: ", lo=1)
        if not run_query("SELECT 1 FROM menu WHERE item_id=%s", (item_id,), fetch=True):
            print("No such item.")
            return
        print("1. Price  2. Stock  3. Show/hide on menu")
        choice = ask_int("What to change: ", lo=1, hi=3)
        if choice == 1:
            run_query("UPDATE menu SET price=%s WHERE item_id=%s", (ask_float("New price: "), item_id))
        elif choice == 2:
            run_query("UPDATE menu SET stock=%s WHERE item_id=%s", (ask_int("New stock: ", lo=0), item_id))
        else:
            run_query("UPDATE menu SET available=%s WHERE item_id=%s",
                      (ask_yes_no("Show on menu?"), item_id))
        print("Updated.")

    def low_stock(self):
        rows = run_query("SELECT item_id, name, stock FROM menu WHERE stock<=10 ORDER BY stock", fetch=True)
        print("Items with stock <= 10:")
        print_table(["ID", "Item", "Stock"], rows)

    # ---------- orders ----------
    def view_orders(self):
        rows = run_query("SELECT o.order_id, u.username, o.order_time, o.total, o.status "
                         "FROM orders o JOIN users u ON o.user_id=u.user_id "
                         "ORDER BY o.order_time DESC LIMIT 30", fetch=True)
        print_table(["Order", "Customer", "Time", "Total", "Status"], rows)

    def update_order_status(self):
        self.view_orders()
        order_id = ask_int("Order ID: ", lo=1)
        print("1. placed  2. preparing  3. served")
        status = ["placed", "preparing", "served"][ask_int("New status: ", lo=1, hi=3) - 1]
        run_query("UPDATE orders SET status=%s WHERE order_id=%s", (status, order_id))
        print("Status updated.")

    # ---------- feedback & complaints ----------
    def view_feedback(self):
        rows = run_query("SELECT f.feedback_id, u.username, f.type, f.rating, f.comments, "
                         "IF(f.resolved,'Yes','No') FROM feedback f JOIN users u ON f.user_id=u.user_id "
                         "ORDER BY f.resolved, f.created_at DESC", fetch=True)
        print_table(["ID", "Customer", "Type", "Rating", "Comments", "Resolved"], rows)
        if rows and ask_yes_no("Mark one as resolved?"):
            run_query("UPDATE feedback SET resolved=1 WHERE feedback_id=%s", (ask_int("Feedback ID: ", lo=1),))
            print("Marked resolved.")

    # ---------- sales ----------
    def sales_report(self):
        revenue, count = run_query("SELECT COALESCE(SUM(total),0), COUNT(*) FROM orders", fetch=True)[0]
        print(f"\nTotal revenue: {revenue}   Total orders: {count}")

        print("\nLast 7 days:")
        print_table(["Date", "Orders", "Revenue"], run_query(
            "SELECT DATE(order_time), COUNT(*), SUM(total) FROM orders "
            "GROUP BY DATE(order_time) ORDER BY 1 DESC LIMIT 7", fetch=True))

        print("\nTop 5 selling items:")
        print_table(["Item", "Qty sold"], run_query(
            "SELECT m.name, SUM(oi.quantity) AS q FROM order_items oi "
            "JOIN menu m ON oi.item_id=m.item_id GROUP BY m.item_id, m.name "
            "ORDER BY q DESC LIMIT 5", fetch=True))

        avg = run_query("SELECT ROUND(AVG(rating),2) FROM feedback WHERE type='feedback'", fetch=True)[0][0]
        print(f"\nAverage customer rating: {avg if avg is not None else 'no ratings yet'}")

    # ---------- main loop ----------
    def menu_loop(self):
        actions = {
            1: self.view_menu, 2: self.add_item, 3: self.update_item, 4: self.low_stock,
            5: self.view_orders, 6: self.update_order_status, 7: self.view_feedback, 8: self.sales_report,
        }
        while True:
            print(f"\n--- Admin Dashboard ({self.username}) ---")
            print("1. View menu\n2. Add item\n3. Update item (price/stock/visibility)\n4. Low-stock alert\n"
                  "5. View orders\n6. Update order status\n7. Feedback & complaints\n8. Sales report\n0. Logout")
            choice = ask_int("Choice: ", lo=0, hi=8)
            if choice == 0:
                break
            actions[choice]()
