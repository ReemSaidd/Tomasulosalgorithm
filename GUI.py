from Alg import Tomasulos_Algorithm
from tkinter import Tk, Button, Entry, filedialog, Label, Text
import tkinter as tk

class StartWindow:
    def __init__(self):
        super().__init__()
        self.root = Tk()
        self.root.title("Tomasulos Algorithm")
        self.root.geometry("400x400")
        self.inputfile = ""
        self.instructionLabel = ""
        self.instructionEntry = Label(self.root)
        self.instructionEntry.pack()

    def selectFile(self):
        self.root = Tk()
        self.root.withdraw()
        self.inputfile = filedialog.askopenfilename()
        if self.inputfile:
            print("The selected file", self.inputfile)
        else:
            self.inputfile = ""
            print("No file selected")
        self.root.destroy()


    def executeFile(self):
        print(self.inputfile)
        if self.inputfile:
            algorithm = Tomasulos_Algorithm()
            algorithm.readInstructionsFromFile(self.inputfile)
            self.root = EducationalWindow(algorithm.Reservation_Stations, algorithm.registerFile, algorithm)
            self.root.update_labels(algorithm.Clock)
            self.root.mainloop()
        else:
            print("No file executing")

    def submitInstructions(self):
        #SW = StartWindow() ##?
        instructions = self.instructionEntry.get()
        instructionsList = instructions.split(';')
        self.saveInstructions(instructionsList)

        print("Entered instructions: ", instructions)



    def saveInstructions(self, instructionsList):
        file_name = "instructions.txt"
        instructions = "\n".join(instructionsList)
        with open(file_name, 'w') as file:
            file.write(instructions)
        print("Instructions saved to", file_name)

        algorithm = Tomasulos_Algorithm()
        algorithm.readInstructionsFromFile(file_name)
        EW = EducationalWindow(algorithm.Reservation_Stations, algorithm.registerFile, algorithm)
    
    
    def test(self):
        fileSelectButton = Button(text = "Select the file", command =self.selectFile)
        fileSelectButton.pack()


        fileButton = Button(self.root, text = "Execute File Code: ", command =self.executeFile)
        fileButton.pack()

        submitButton = Button(self.root, text = "Execute Written Code: ", command = self.submitInstructions)
        submitButton.pack()

        instructionLabel = Label(self.root, text = "Enter Instructions: ")
        instructionLabel.pack()

        self.instructionEntry = Entry(self.root)
        self.instructionEntry.pack()

        self.root.mainloop()


class EducationalWindow(tk.Tk):
    def __init__(self, reservation_stations, register_file, algorithm):
        super().__init__()

        self.reservation_stations = reservation_stations
        self.register_file = register_file
        self.algorithm = algorithm
        self.title("Learn.")
        self.memory_label = tk.Label(self, text="Memory Content:\n")
        self.memory_label.grid(row=len(self.reservation_stations) + 5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(9, weight=1)

        self.station_labels = []
        for i, station in enumerate(self.reservation_stations):
            label_text = f"{station.Name}: Op={station.Op}, Vj={station.Vj}, Vk={station.Vk}, Qj={station.Qj}, Qk={station.Qk}, Busy={station.Busy}, A={station.A}"
            label = tk.Label(self, text=label_text)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.station_labels.append(label)

        self.register_labels = []
        for i in range(8):
            label_text = f"R{i}: Value={self.register_file.getRegisterVal(f'R{i}')}, Qi={self.register_file.getRegisterQ(f'R{i}')}"
            label = tk.Label(self, text=label_text)
            label.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.register_labels.append(label)

        self.ipc_label = tk.Label(self, text="IPC: ")
        self.ipc_label.grid(row=len(self.reservation_stations) + 1, column=0, padx=10, pady=5, sticky="e")
        self.prediction_label = tk.Label(self, text="Prediction: ")
        self.prediction_label.grid(row=len(self.reservation_stations) + 1, column=1, padx=10, pady=5, sticky="w")

        solid_line = tk.Frame(self, height=2, bd=1, relief=tk.SOLID)
        solid_line.grid(row=len(self.reservation_stations) + 2, column=0, columnspan=2, padx=10, pady=5, sticky="we")

        clock_label = tk.Label(self, text="Clock Cycle:")
        clock_label.grid(row=len(self.reservation_stations) + 3, column=0, padx=10, pady=5, sticky="e")
        self.clock_value_label = tk.Label(self, text="0")
        self.clock_value_label.grid(row=len(self.reservation_stations) + 3, column=1, padx=10, pady=5, sticky="e")

        start_button = tk.Button(self, text="Start Cycle", command=self.start_cycle)
        start_button.grid(row=len(self.reservation_stations) + 4, column=0, columnspan=2, padx=10, pady=5)

    def update_labels(self, clock_cycle):
        for i, station in enumerate(self.reservation_stations):
            label_text = f"{station.Name}: Op={station.Op}, Vj={station.Vj}, Vk={station.Vk}, Qj={station.Qj}, Qk={station.Qk}, Busy={station.Busy}, A={station.A}"
            self.station_labels[i].config(text=label_text)

        for i in range(8):
            label_text = f"R{i}: Value={self.register_file.getRegisterVal(f'R{i}')}, Qi={self.register_file.getRegisterQ(f'R{i}')}"
            self.register_labels[i].config(text=label_text)

        self.clock_value_label.config(text=clock_cycle)

    def start_cycle(self):
        self.algorithm.startCycle()
        self.update_labels(self.algorithm.Clock)
        self.update_ipc_label()
        self.update_prediction_label()
        self.update_memory_label()  # Update the memory label

    def update_ipc_label(self):
        ipc = self.algorithm.getIPC()  # Replace this with the actual method to get IPC from your algorithm
        self.ipc_label.config(text=f"IPC: {ipc}")

    def update_memory_label(self):
        memory_content = ""
        for address, value in self.algorithm.showMemory().items():
            memory_content += f"address: {address}, value: {value}\n"
        self.memory_label.config(text="Memory Content:\n" + memory_content)

    def update_prediction_label(self):
        prediction = self.algorithm.getPrediction()  # Replace this with the actual method to get the prediction from your algorithm
        self.prediction_label.config(text=f"Fail Percentage: {prediction}%")

start = StartWindow()
start.test()
