from Alg import Tomasulos_Algorithm as TA
from tkinter import Tk, Button, Entry, filedialog,ttk
import tkinter as tk

class EducationalWindow(tk.Tk):
    def __init__(self, root):
        table = ttk.Treeview(root)

        # Define columns
        table["columns"] = ("Name", "Busy", "Op", "Vj", "Vk", "Qj", "Qk", "A")  #add status later

        # Format column headers
        table.heading("Name", text="Name")
        table.heading("Busy", text="Busy")
        table.heading("Op", text="Op")
        table.heading("Vj", text="Vj")
        table.heading("Vk", text="Vk")
        table.heading("Qj", text="Qj")
        table.heading("Qk", text="Qk")
        table.heading("A", text="A")

        # Add data rows

        table.insert("", "end", values=("John Doe", 25, "New York"))
        table.insert("", "end", values=("Jane Smith", 30, "London"))
        table.insert("", "end", values=("Bob Johnson", 40, "Paris"))

        # Display table
        table.pack()
def create_table(root):
    table = ttk.Treeview(root)

    # Define columns
    table["columns"] = ("Name", "Busy", "Op", "Vj", "Vk", "Qj", "Qk", "A")  #add status later

    # Format column headers
    table.heading("Name", text="Name")
    table.heading("Busy", text="Busy")
    table.heading("Op", text="Op")
    table.heading("Vj", text="Vj")
    table.heading("Vk", text="Vk")
    table.heading("Qj", text="Qj")
    table.heading("Qk", text="Qk")
    table.heading("A", text="A")

    # Add data rows

    table.insert("", "end", values=("John Doe", 25, "New York"))
    table.insert("", "end", values=("Jane Smith", 30, "London"))
    table.insert("", "end", values=("Bob Johnson", 40, "Paris"))

    # Display table
    table.pack()

# Create root window
root = tk.Tk()

# Call the function to create the table
create_table(root)

# Start the Tkinter event loop
root.mainloop()
