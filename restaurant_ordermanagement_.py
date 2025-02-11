# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:10:45 2024

@author: 91967
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import matplotlib.pyplot as plt
import sqlite3


menu = {
    "Starters": [("Samosa", 50), ("Paneer Tikka", 120), ("Veg Soup", 80)],
    "Main Course": [("Paneer Butter Masala", 200), ("Dal Makhani", 150), ("Naan", 40)],
    "Juices": [("Mango Juice", 70), ("Lime Juice", 50)],
    "Desserts": [("Gulab Jamun", 90), ("Rasmalai", 100)]
}
order_queue = []  
orders = {}
payments = {}  
sales_data = {category: {item[0]: 0 for item in items} for category, items in menu.items()}  # Sales tracking
feedback_data = []


admin_password = "amrita123"


def setup_database():
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            order_type TEXT NOT NULL,
            table_number TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

setup_database()


class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Amrita Bhavan - Restaurant Management System")
        self.main_menu()

    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Welcome to Amrita Bhavan", font=("Arial", 24))
        label.pack(pady=20)

        admin_btn = tk.Button(self.root, text="Admin Login", command=self.admin_login)
        admin_btn.pack(pady=10)

        user_btn = tk.Button(self.root, text="User   Login", command=self.user_login)
        user_btn.pack(pady=10)

        feedback_btn = tk.Button(self.root, text="Feedback", command=self.collect_feedback)
        feedback_btn.pack(pady=10)

    def admin_login(self):
        password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show='*')
        if password == admin_password:
            self.admin_panel()
        else:
            messagebox.showerror("Error", "Invalid Password!")

    def admin_panel(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Admin Panel", font=("Arial", 20))
        label.pack(pady=10)

        view_orders_btn = tk.Button(self.root, text="View Orders", command=self.view_orders)
        view_orders_btn.pack(pady=10)

        update_menu_btn = tk.Button(self.root, text="Update Menu", command=self.update_menu)
        update_menu_btn.pack(pady=10)

        verify_payment_btn = tk.Button(self.root, text="Verify Payments", command=self.verify_payment)
        verify_payment_btn.pack(pady=10)

        check_payment_status_btn = tk.Button(self.root, text="Check Payment Status", command=self.check_payment_status)
        check_payment_status_btn.pack(pady=10)

        complete_order_btn = tk.Button(self.root, text="Mark Order as Completed", command=self.mark_order_completed)
        complete_order_btn.pack(pady=10)

        sales_report_btn = tk.Button(self.root, text="View Sales Report", command=self.view_sales_report)
        sales_report_btn.pack(pady=10)

        feedback_btn = tk.Button(self.root, text="View Feedback", command=self.view_feedback)
        feedback_btn.pack(pady=10)

        back_btn = tk.Button(self.root, text="Back to Main Menu", command=self.main_menu)
        back_btn.pack(pady=10)

    def view_feedback(self):
        if feedback_data:
            feedback_text = "\n".join([f"Table: {fb[0]} | Rating: {fb[1]} stars" for fb in feedback_data])
            messagebox.showinfo("Customer Feedback", feedback_text)
        else:
            messagebox.showinfo("Customer Feedback", "No Feedback Available")

    def view_orders(self):
        dine_in_orders = [o for o in order_queue if o['order_type'] == 'dine-in']
        takeaway_orders = [o for o in order_queue if o['order_type'] == 'takeaway']
        
        orders_text = "\n".join([f"Table: {o['table']} | Items: {', '.join(o['items'])} | Status: {'Paid' if o['paid'] else 'Pending'}" for o in dine_in_orders + takeaway_orders])
        messagebox.showinfo("Current Orders", orders_text if orders_text else "No Orders Available")

    def update_menu(self):
        action = simpledialog.askstring("Update Menu", "Type 'add' to add an item or 'delete' to remove an item:")
        if action and action.lower() == 'add':
            item = simpledialog.askstring("Add Item", "Enter Item Name:")
            price = simpledialog.askinteger("Add Item", "Enter Item Price:")
            category = simpledialog.askstring("Add Item", "Enter Category (Starters, Main Course, Juices, Desserts):")

            if category in menu:
                menu[category].append((item, price))
                messagebox.showinfo("Success", f"{item} added to {category}!")
            else:
                messagebox.showerror("Error", "Invalid Category!")

        elif action and action.lower() == 'delete':
            item_to_delete = simpledialog.askstring("Delete Item", "Enter Item Name to Delete:")
            item_found = False
            for category in menu:
                for item in menu[category]:
                    if item[0].lower() == item_to_delete.lower():
                        menu[category].remove(item)
                        item_found = True
                        messagebox.showinfo("Success", f"{item_to_delete} removed from {category}!")
                        break
                if item_found:
                    break

            if not item_found:
                messagebox.showerror("Error", f"{item_to_delete} not found in menu.")

    def verify_payment(self):
        table = simpledialog.askstring("Verify Payment", "Enter Table Number:")
        if table in payments and not payments[table]:
            payments[table] = True
            messagebox.showinfo("Payment", f"Payment for Table {table} marked as PAID.")
        else:
            messagebox.showerror("Error", "Invalid Table or Already Paid")

    def check_payment_status(self):
        payment_status_text = "\n".join([f"Table {table}: {'Paid' if paid else 'Pending'}" for table, paid in payments.items()])
        messagebox.showinfo("Payment Status", payment_status_text if payment_status_text else "No Payments Recorded")

    def mark_order_completed(self):
        table = simpledialog.askstring("Complete Order", "Enter Table Number:")
        for order in order_queue:
            if order['table'] == table:
                if payments.get(table, False):
                    order_queue.remove(order)
                    messagebox.showinfo("Order", f"Order for Table {table} completed!")
                else:
                    messagebox.showerror("Error", "Payment not verified!")
                return
        messagebox.showerror("Error", "Invalid Table Number!")

    def user_login(self):
        dine_or_takeaway = simpledialog.askstring("Dining Option", "Dine-in or Takeaway:")
        if dine_or_takeaway and dine_or_takeaway.lower() == 'dine-in':
            table_number = simpledialog.askstring("Dine-in", "Enter Table Number:")
            self.take_order(table_number, 'dine-in')
        elif dine_or_takeaway and dine_or_takeaway.lower() == 'takeaway':
            name = simpledialog.askstring("Takeaway", "Enter Your Name:")
            phone = simpledialog.askstring("Takeaway", "Enter 10-Digit Phone Number:")
            if len(phone) == 10 and phone.isdigit():
                table_number = str(random.randint(20, 40))  # Assign a random table number between 20 and 40
                messagebox.showinfo("Takeaway Assigned", f"Takeaway assigned to Table {table_number}")
                self.save_customer_details(name, phone, 'takeaway', table_number)
                self.take_order(table_number, 'takeaway')
            else:
                messagebox.showerror("Error", "Invalid Phone Number!")

    def collect_feedback(self):
        table_number = simpledialog.askstring("Feedback", "Enter Table Number:")
        rating = simpledialog.askinteger("Feedback", "Rate us out of 5 stars:", minvalue=1, maxvalue=5)
        if rating is not None:
            feedback_data.append((table_number, rating))  # Store feedback
            messagebox.showinfo("Thank You!", f"Thank you for your feedback! You rated us {rating} stars.")
        self.main_menu()

    def take_order(self, table_number, order_type):
        for widget in self.root.winfo_children():
            widget.destroy()

        order_items = []
        total_cost = 0

        def add_item(category, item, price):
            nonlocal total_cost
            order_items.append(item)
            total_cost += price
            label.config(text=f"Selected Items: {', '.join(order_items)}\nTotal: ₹{total_cost}")

        label = tk.Label(self.root, text="Select Items from Menu", font=("Arial", 16))
        label.pack(pady=10)

        for category, items in menu.items():
            category_label = tk.Label(self.root, text=category, font=("Arial", 14, "bold"))
            category_label.pack(pady=5)
            for item, price in items:
                item_btn = tk.Button(self.root, text=f"{item} - ₹{price}", command=lambda i=item, p=price, c=category: add_item(c, i, p))
                item_btn.pack(pady=2)

        def place_order():
            if order_items:
                order_queue.append({"table": table_number, "items": order_items, "paid": False, "order_type": order_type})
                payments[table_number] = False
                est_time = len(order_items) * 5  # Estimate time based on the number of items
                messagebox.showinfo("Order Placed", f"Your order will be ready in {est_time} minutes.")
                self.select_payment_method(table_number)
                for item in order_items:
                    for category, items in menu.items():
                        for i, p in items:
                            if i == item:
                                sales_data[category][item] += 1
            else:
                messagebox.showerror("Error", "No items selected!")

        place_order_btn = tk.Button(self.root, text="Place Order", command=place_order)
        place_order_btn.pack(pady=20)

    def select_payment_method(self, table_number):
        payment_method = simpledialog.askstring("Payment", "Select Payment Method (Cash/Card/UPI):")
        
        
        if payment_method is None:
            messagebox.showerror("Error", "Payment method not selected!")
            return  
        
        if payment_method.lower() in ['cash', 'card', 'upi']:
            messagebox.showinfo("Payment", f"Payment method selected: {payment_method}. Please pay at the counter.")
            messagebox.showinfo("Order Complete", f"Order placed for Table {table_number}.")
            self.main_menu()  
        else:
            messagebox.showerror("Error", "Invalid Payment Method!")

    def save_customer_details(self, name, phone, order_type, table_number):
        conn = sqlite3.connect('customers.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, phone, order_type, table_number)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, order_type, table_number))
        conn.commit()
        conn.close()

    def view_sales_report(self):
        total_earnings = sum([sum([price * sales_data[category][item] for item, price in items]) for category, items in menu.items()])
        messagebox.showinfo("Sales Report", f"Total Earnings: ₹{total_earnings}")

        
        category_sales = {category: sum([price * sales_data[category][item] for item, price in items]) for category, items in menu.items()}
        highest_selling_category = max(category_sales, key=category_sales.get)


        item_sales = {item: price * sales_data[highest_selling_category][item] for item, price in menu[highest_selling_category]}

        
        plt.bar(item_sales.keys(), item_sales.values())
        plt.xlabel("Item")
        plt.ylabel("Sales")
        plt.title(f"Sales of {highest_selling_category} Items")
        plt.show()

        
        plt.pie(category_sales.values(), labels=category_sales.keys(), autopct='%1.1f%%')
        plt.title("Category Sales")
        plt.show()


root = tk.Tk()
app = RestaurantApp(root)
root.mainloop()