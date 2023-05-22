from Alg import Tomasulos_Algorithm as TA
from tkinter import Tk, Button, Entry, filedialog,ttk
import tkinter as tk

class EducationalWindow(tk.Tk):
    def __init__(self, root, TA):
        table = ttk.Treeview(root)
        self.TA = TA

        # Define columns
        table["columns"] = ("Name", "Busy", "Vj", "Vk", "Qj", "Qk", "A")  #add status later

        # Format column headers
        table.heading("Name", text="Name")
        table.heading("Busy", text="Busy")
        table.heading("Vj", text="Vj")
        table.heading("Vk", text="Vk")
        table.heading("Qj", text="Qj")
        table.heading("Qk", text="Qk")
        table.heading("A", text="A")

        # Configure column widths
        table.column("Name", width=100)  # Adjust the width as needed
        table.column("Busy", width=50)
        table.column("Vj", width=50)
        table.column("Vk", width=50)
        table.column("Qj", width=50)
        table.column("Qk", width=50)
        table.column("A", width=50)

        # Add data rows
        for i, station in enumerate(self.TA.Reservation_Stations):
            table.insert("", "end", values=(station.Name, station.Busy, station.Vj, station.Vk, station.Qj, station.Qk, station.A))

        # Display table
        table.pack()

class Initial_Screen(tk.Tk):
    def __init__(self):
        self.title = "Tomasulo's Algorithm"
        self.geometry = "500x500"
        self.root = Tk()

        self.title_label = tk.Label(self, text="Enter instructions below")
        self.title_label.pack()

        self.instruction_entry = tk.Entry(self.root)
        self.instruction_entry.pack()

        self.instruction_button = tk.Button(self.root, text="Add Instruction", command=self.add_instruction)
        self.instruction_button.pack()


# Create an instance of the home screen
# home_screen = Initial_Screen()

# # Start the Tkinter event loop
# home_screen.mainloop()
# # Create root window
# root = tk.Tk()

# alg = TA()
# # Call the function to create the table
# ED = EducationalWindow( root, alg)

# # Start the Tkinter event loop
# root.mainloop()
