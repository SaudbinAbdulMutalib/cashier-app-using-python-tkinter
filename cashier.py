# cashier_system_tkinter.py

import tkinter as tk
from tkinter import messagebox, scrolledtext # messagebox for alerts, scrolledtext for cart display
import sys

# --- Product Database (in-memory for simplicity) ---
# In a real system, this would come from a database or file.
# Using a dictionary for quick lookup by product ID
PRODUCTS = {
    "101": {"name": "Apple", "price": 1.50},
    "102": {"name": "Banana", "price": 0.75},
    "103": {"name": "Orange", "price": 1.20},
    "201": {"name": "Milk (1L)", "price": 3.00},
    "202": {"name": "Bread", "price": 2.20},
    "301": {"name": "Chocolate Bar", "price": 1.00},
    "302": {"name": "Chips (Large)", "price": 2.50},
    "401": {"name": "Water Bottle", "price": 0.80},
    "501": {"name": "Coffee (Instant)", "price": 5.00},
    "601": {"name": "Soda (Can)", "price": 1.10},
}

TAX_RATE = 0.08 # 8% sales tax
DISCOUNT_PERCENTAGE = 0.10 # 10% discount for orders over $20

class CashierApp:
    def __init__(self, master):
        self.master = master
        master.title("Python Cashier System")
        master.geometry("800x600") # Set initial window size
        master.resizable(True, True) # Allow window resizing

        self.cart = [] # List to store items in the current transaction
        self.subtotal = 0.0
        self.tax_amount = 0.0
        self.discount_amount = 0.0
        self.total_bill = 0.0
        self.amount_paid = 0.0
        self.change = 0.0

        self.create_widgets()
        self.update_display() # Initial display update

    def create_widgets(self):
        """Sets up all the GUI elements for the cashier system."""

        # --- Frame for Product List Display ---
        product_list_frame = tk.LabelFrame(self.master, text="Available Products", padx=10, pady=10)
        product_list_frame.pack(pady=5, padx=10, fill="x")

        self.product_list_display = scrolledtext.ScrolledText(product_list_frame, width=70, height=6, state='disabled', wrap=tk.WORD)
        self.product_list_display.pack(padx=5, pady=5, fill="both", expand=True)
        
        self.populate_product_list_display() # Populate the product list on startup

        # --- Frame for Product Input ---
        input_frame = tk.LabelFrame(self.master, text="Add Item", padx=10, pady=10)
        input_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(input_frame, text="Product ID/Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_entry = tk.Entry(input_frame, width=30)
        self.product_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.product_entry.bind("<Return>", lambda event: self.add_item_to_cart_gui()) # Bind Enter key

        tk.Label(input_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(input_frame, width=10)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.quantity_entry.bind("<Return>", lambda event: self.add_item_to_cart_gui()) # Bind Enter key

        add_button = tk.Button(input_frame, text="Add to Cart", command=self.add_item_to_cart_gui)
        add_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")

        # --- Frame for Cart Display ---
        cart_frame = tk.LabelFrame(self.master, text="Shopping Cart", padx=10, pady=10)
        cart_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.cart_display = scrolledtext.ScrolledText(cart_frame, width=70, height=10, state='disabled', wrap=tk.WORD)
        self.cart_display.pack(padx=5, pady=5, fill="both", expand=True)

        # --- Frame for Totals Display ---
        totals_frame = tk.LabelFrame(self.master, text="Bill Summary", padx=10, pady=10)
        totals_frame.pack(pady=5, padx=10, fill="x")

        self.subtotal_label = tk.Label(totals_frame, text="Subtotal: $0.00", anchor="w")
        self.subtotal_label.pack(fill="x", pady=2)
        self.discount_label = tk.Label(totals_frame, text="Discount: $0.00", anchor="w", fg="red")
        self.discount_label.pack(fill="x", pady=2)
        self.tax_label = tk.Label(totals_frame, text="Tax (8%): $0.00", anchor="w")
        self.tax_label.pack(fill="x", pady=2)
        self.total_label = tk.Label(totals_frame, text="Total: $0.00", font=("Arial", 14, "bold"), anchor="w")
        self.total_label.pack(fill="x", pady=5)

        # --- Frame for Payment ---
        payment_frame = tk.LabelFrame(self.master, text="Payment", padx=10, pady=10)
        payment_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(payment_frame, text="Amount Paid:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.paid_entry = tk.Entry(payment_frame, width=20)
        self.paid_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.paid_entry.bind("<Return>", lambda event: self.process_payment_gui()) # Bind Enter key

        process_button = tk.Button(payment_frame, text="Process Payment", command=self.process_payment_gui)
        process_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.change_label = tk.Label(payment_frame, text="Change: $0.00", font=("Arial", 14, "bold"), fg="blue", anchor="w")
        self.change_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # --- Action Buttons ---
        action_frame = tk.Frame(self.master, padx=10, pady=5)
        action_frame.pack(pady=5, padx=10, fill="x")

        clear_button = tk.Button(action_frame, text="Clear Cart", command=self.clear_cart)
        clear_button.pack(side="left", padx=5)

        exit_button = tk.Button(action_frame, text="Exit", command=self.master.quit)
        exit_button.pack(side="right", padx=5)

        # --- Message Display ---
        self.message_label = tk.Label(self.master, text="", fg="green", wraplength=750)
        self.message_label.pack(pady=5, padx=10, fill="x")

    def populate_product_list_display(self):
        """Populates the scrolled text widget with the list of available products."""
        self.product_list_display.config(state='normal') # Enable editing
        self.product_list_display.delete(1.0, tk.END) # Clear current content

        self.product_list_display.insert(tk.END, f"{'ID':<5} {'Product Name':<20} {'Price':<8}\n")
        self.product_list_display.insert(tk.END, "-"*35 + "\n")
        
        for p_id, p_data in PRODUCTS.items():
            self.product_list_display.insert(tk.END, 
                f"{p_id:<5} {p_data['name']:<20} ${p_data['price']:.2f}\n"
            )
        
        self.product_list_display.config(state='disabled') # Disable editing

    def display_message(self, message, is_error=False):
        """Displays a message to the user in the message label."""
        self.message_label.config(text=message, fg="red" if is_error else "green")
        # Clear message after a few seconds
        self.master.after(5000, lambda: self.message_label.config(text=""))

    def find_product(self, query):
        """Finds a product by ID or (partial) name."""
        # Try exact ID match first
        if query in PRODUCTS:
            return PRODUCTS[query]
        
        # Then try partial name match (case-insensitive)
        query_lower = query.lower()
        found_products = [
            p_data for p_id, p_data in PRODUCTS.items() 
            if query_lower in p_data["name"].lower()
        ]

        if len(found_products) == 1:
            return found_products[0]
        elif len(found_products) > 1:
            self.display_message(f"Multiple products found for '{query}'. Please be more specific or use Product ID.", True)
            return None
        else:
            return None # No product found

    def add_item_to_cart_gui(self):
        """Adds an item to the cart based on GUI input."""
        product_query = self.product_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()

        if not product_query:
            self.display_message("Please enter a Product ID or Name.", True)
            return
        if not quantity_str:
            self.display_message("Please enter a Quantity.", True)
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                self.display_message("Quantity must be a positive number.", True)
                return
        except ValueError:
            self.display_message("Invalid quantity. Please enter a number.", True)
            return

        product = self.find_product(product_query)
        if product is None:
            # Message already displayed by find_product if multiple found
            if not self.message_label.cget("text"): # Only display if no other message
                self.display_message(f"Product '{product_query}' not found.", True)
            return

        line_total = product["price"] * quantity
        self.cart.append({
            "product_name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "line_total": line_total
        })
        self.display_message(f"Added {quantity} x {product['name']} to cart.")
        self.product_entry.delete(0, tk.END) # Clear input fields
        self.quantity_entry.delete(0, tk.END)
        self.product_entry.focus_set() # Set focus back to product entry
        self.update_display()

    def calculate_bill(self):
        """Calculates subtotal, discount, tax, and total bill."""
        self.subtotal = sum(item["line_total"] for item in self.cart)

        self.discount_amount = 0.0
        if self.subtotal >= 20.00: # Apply discount if subtotal meets threshold
            self.discount_amount = self.subtotal * DISCOUNT_PERCENTAGE
            
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * TAX_RATE
        self.total_bill = taxable_amount + self.tax_amount

    def update_display(self):
        """Updates the cart display and bill summary labels."""
        self.calculate_bill()

        # Update cart display
        self.cart_display.config(state='normal') # Enable editing
        self.cart_display.delete(1.0, tk.END) # Clear current content

        if not self.cart:
            self.cart_display.insert(tk.END, "Cart is empty.\n")
        else:
            self.cart_display.insert(tk.END, f"{'Item':<20} {'Qty':<5} {'Price':<8} {'Total':<8}\n")
            self.cart_display.insert(tk.END, "-"*50 + "\n")
            for item in self.cart:
                self.cart_display.insert(tk.END, 
                    f"{item['product_name']:<20} {item['quantity']:<5} ${item['price']:.2f}{'<':<7} ${item['line_total']:.2f}\n"
                )
            self.cart_display.insert(tk.END, "-"*50 + "\n")
        
        self.cart_display.config(state='disabled') # Disable editing

        # Update totals labels
        self.subtotal_label.config(text=f"Subtotal: ${self.subtotal:.2f}")
        self.discount_label.config(text=f"Discount: -${self.discount_amount:.2f}")
        self.tax_label.config(text=f"Tax ({TAX_RATE*100:.0f}%): ${self.tax_amount:.2f}")
        self.total_label.config(text=f"Total: ${self.total_bill:.2f}")
        self.change_label.config(text="Change: $0.00") # Reset change until payment

    def process_payment_gui(self):
        """Processes payment based on GUI input."""
        paid_str = self.paid_entry.get().strip()

        if not self.cart:
            self.display_message("Cart is empty. Please add items first.", True)
            return
        if not paid_str:
            self.display_message("Please enter the amount paid.", True)
            return

        try:
            self.amount_paid = float(paid_str)
            if self.amount_paid < self.total_bill:
                self.display_message(f"Amount paid (${self.amount_paid:.2f}) is less than total bill (${self.total_bill:.2f}).", True)
                return
        except ValueError:
            self.display_message("Invalid amount paid. Please enter a number.", True)
            return

        self.change = self.amount_paid - self.total_bill
        self.change_label.config(text=f"Change: ${self.change:.2f}")
        self.display_message(f"Payment successful! Change: ${self.change:.2f}")
        
        # Optionally, clear cart after successful payment
        messagebox.showinfo("Payment Complete", 
                            f"Total: ${self.total_bill:.2f}\nPaid: ${self.amount_paid:.2f}\nChange: ${self.change:.2f}\n\nTransaction Complete!")
        self.clear_cart() # Start a new transaction

    def clear_cart(self):
        """Clears the current shopping cart and resets all totals."""
        self.cart = []
        self.subtotal = 0.0
        self.tax_amount = 0.0
        self.discount_amount = 0.0
        self.total_bill = 0.0
        self.amount_paid = 0.0
        self.change = 0.0
        self.paid_entry.delete(0, tk.END)
        self.update_display()
        self.display_message("Cart cleared. Ready for new transaction.")


# --- Main Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk() # Create the main Tkinter window
    app = CashierApp(root) # Create an instance of our CashierApp
    root.mainloop() # Start the Tkinter event loop

