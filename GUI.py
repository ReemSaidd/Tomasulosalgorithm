from Alg import Tomasulos_Algorithm as TA
from tkinter import Tk, Button, Entry, filedialog,ttk
import tkinter as tk

class EducationalWindow(tk.Tk):
    def __init__(self, root, TA):
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
        for i, station in enumerate(TA.Reservation_Stations):
            table.insert("", "end", values=(station[i].Name, station.Busy, station.Op, station.Vj, station.Vk, station.Qj, station.Qk, station.A))

        # Display table
        table.pack()
def create_table(root, TA):
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
    for station in enumerate(TA.Reservation_Stations):
        table.insert("", "end", values=(station.Name, station.Busy, station.Op, station.Vj, station.Vk, station.Qj, station.Qk, station.A))


    # Display table
    table.pack()

# Create root window
root = tk.Tk()

alg = TA()
# Call the function to create the table
create_table(root, alg)

# Start the Tkinter event loop
root.mainloop()
