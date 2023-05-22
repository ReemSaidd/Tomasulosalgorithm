from Classes import Reservation_Station, Register_File
from tkinter import Tk, Button, Entry, filedialog, Label
import tkinter as tk

class Tomasulos_Algorithm:
    def __init__(self):
        self.Reservation_Stations = [ #creating stations required
            Reservation_Station("Load1", "LOAD",2), Reservation_Station("Load2", "LOAD",2),
            Reservation_Station("Store1", "STORE",2),Reservation_Station("Store2", "STORE",2),
            Reservation_Station("Bne1", "BNE",1),
            Reservation_Station("Jal1", "JAL",1),
            Reservation_Station("Add1", "ADD",2), Reservation_Station("Add2", "ADD", 2),Reservation_Station("Add3", "ADD", 2),
            Reservation_Station("Neg1", "NEG",2),
            Reservation_Station("Nand1", "NAND",1),
            Reservation_Station("Sll1", "SLL",8)
            ]
        self.pc = -1 #before we do anything pc is not even 0 yet
        self.finished = 0 #variable to aid ipc calculation, now ipc is simply finished / cycles

        ## branch logic
        self.branchDirty =0
        self.success = 0
        self.fail = 0

        ## jumping logic
        self.takeIn = True

        self.registerFile= Register_File()
        self.Clock = 0
        self.instructions = []
        self.Memory = {}
        self.instructionsOrg = [] #used to store the instructions since we will be popping and we need the original incase of branching and jumping
        self.labelMap = {} #used to map labels to index in file
        self.StoreLoadPriority = []
    def readInstructionsFromFile(self, instfile):
        """
         there is an assumption user must put label in the same line for example

         branch:
         add x0,x0,x0  is not allowed

         but
         branch: add x0,x0,x0 is allowed
        """
        with open(instfile, 'r') as file:
            index = 0
            for line in file:
                line = line.strip()
                if line:
                    if ':' in line:
                        parts = line.split(':', 1) #split along the :
                        label = parts[0].strip() #left side is 0
                        instruction = parts[1].strip() #right side is 1
                        self.labelMap[label] = index #store labels into map so that I can simply do map[labelname] and that will get me the place it is in the inst memory
                        self.instructions.append(instruction) #put the instruction without the lavel in the inst memory no need to keep track of label anymore since we have the place it is  in

                    else:
                        self.instructions.append(line) #no : no label put it normally
                    index += 1 #index is where i keep track of the place i am in the inst memory
        self.instructionsOrg = self.instructions.copy()
    def readMemoryFile(self,memfile):
        with open(memfile, 'r') as file:
            for line in file:
                line = line.strip()
                newline = line.split()
                self.Memory[newline[0]] = newline[1]
    def readNext(self):
        if self.instructions:
            self.pc +=1
            return self.instructions.pop(0) #simply pop the last instruction, since we will store it in a var in start cycle we wont lose it
        else:
            return None #in this case we know theres nothing left to read useful for termination
    def checkStation(self,op):
        for station in self.Reservation_Stations:
            if op == station.Op and station.Busy ==0:
                if self.branchDirty:
                    station.waitBranch =1
                return station
        return None
    def printStation(self):
        for station in self.Reservation_Stations:
            print(station.Name + ' ' + str(station.Vj) + ' ' + station.Qj + ' ' + str(station.Vk) + ' ' + (station.Qk))

    def setVQ(self,station:Reservation_Station,*args): #we assume the arguments are put in order so j then k
        index = 0
        for argument in args:
            if self.registerFile.getRegisterQ(argument) != "" and self.registerFile.getRegisterQ(argument)!=station.Name:
                if index ==0:
                    if argument == "R0": #dont be busy we already know R0 must be 0 so we can cut some waiting time
                        station.setValues(Vj = 0)
                    else:
                        station.setValues(Qj = self.registerFile.getRegisterQ(argument))
                else:
                    if argument == "R0": #dont be busy we already know R0 must be 0 so we can cut some waiting time
                        station.setValues(Vk = 0)
                    station.setValues(Qk = self.registerFile.getRegisterQ(argument))
            else:
                if index ==0:
                    station.setValues(Vj = int(self.registerFile.getRegisterVal(argument)))
                else:
                    station.setValues(Vk = int(self.registerFile.getRegisterVal(argument)))
            index+=1
    def updateRD(self,name,value):
        for register in self.registerFile.Registers:
            if register.Qi == name:
                register.Qi = ""
                register.Value = value
    def updateAffected(self,value,finishStation:Reservation_Station):
        for station in self.Reservation_Stations:
            if station.Qj == finishStation.Name:
                station.Qj = ""
                station.Vj = value

            elif station.Qk == finishStation.Name:
                station.Qk = ""
                station.Vk = value
            if finishStation.Op == "ADDI":
                finishStation.Op = "ADD"
            if finishStation.Op == "RET":
                finishStation.Op = "JAL"
        self.resetStation(finishStation)
    def resetStation(self, finishStation:Reservation_Station):
        finishStation.Vj = 0
        finishStation.Vk = 0
        finishStation.Qj = ""
        finishStation.Qk = ""
        finishStation.Busy = 0
        finishStation.A = 0
        finishStation.currCycle=0
        if finishStation.Op == "ADDI":
            finishStation.Op = "ADD"
        if finishStation.Op == "RET":
            finishStation.Op = "JAL"
    def updateBranchSuccess(self):
        self.fail+=1 #our branch predictor is not taken so a branch success is a predictor fail
        for station in self.Reservation_Stations:
            if station.waitBranch == 1:
                for reg in self.registerFile.Registers:
                    if(reg.Qi == station.Name):
                        reg.Qi = ""
                station.Vj = 0
                station.Vk = 0
                station.Qj = ""
                station.Qk = ""
                station.Busy = 0
                station.A = 0
                station.currCycle=0
                if station.Op == "ADDI":
                    station.Op = "ADD"
                if station.Op == "RET":
                    station.Op = "JAL"
                station.waitBranch =0
        self.branchDirty = 0
    def updateBranchFail(self):
        self.success+=1 #our branch predictor is not taken so a branch success is a predictor fail
        self.branchDirty = 0
        for station in self.Reservation_Stations:
            if station.waitBranch == 1:
                station.waitBranch =0
    def handleOp(self,station:Reservation_Station):
        if(station.Op == "LOAD" and station.currCycle >= station.maxCycle): #we do greater than because the cycles of the station keeps increasing when its waiting on dependencies
            val = self.Memory.get(int(station.A)) or 0
            self.updateRD(station.Name, val)
            self.updateAffected(val,station)
        elif(station.Op == "LOAD" and station.currCycle == 1):
            station.A = int(station.A) + station.Vj
            for dep in self.StoreLoadPriority:
                name, _, _ = dep
                if name == station.Name:
                    self.StoreLoadPriority[self.StoreLoadPriority.index(dep)] = (name, station.A, 1)
        elif(station.Op == "STORE" and station.currCycle >= station.maxCycle):  #we do greater than because the cycles of the station keeps increasing when its waiting on dependencies
            self.Memory[station.A] = station.Vk
            self.resetStation(station)
        elif(station.Op == "STORE" and station.currCycle == 1):
            station.A = int(station.A) + station.Vj
            for dep in self.StoreLoadPriority:
                name, _, _ = dep
                if name == station.Name:
                    self.StoreLoadPriority[self.StoreLoadPriority.index(dep)] = (name, int(station.A), 1)
        elif(station.Op == "ADDI"):
            val = station.Vj + int(station.A)
            self.updateRD(station.Name, val)
            self.updateAffected(val,station)
        elif(station.Op == "ADD"):
            val = station.Vj + station.Vk
            self.updateRD(station.Name,val)
            self.updateAffected(val,station)
        elif(station.Op == "NEG"):
            val = -1*station.Vj
            self.updateRD(station.Name,val)
            self.updateAffected(val,station)
        elif(station.Op == "NAND"):
            val = ~(station.Vj &station.Vk)
            self.updateRD(station.Name,val)
            self.updateAffected(val,station)
        elif(station.Op == "SLL"):
            val = station.Vj << station.Vk
            self.updateRD(station.Name,val)
            self.updateAffected(val,station)
        elif(station.Op == "BNE"):
            if station.Vj!= station.Vk:
                self.updateBranchSuccess()
                self.goState(int(station.A))
                self.resetStation(station)
            else:
                self.updateBranchFail()
                self.resetStation(station)
                self.success+=1
        elif(station.Op == "JAL"):
            self.goState(station.A)
            self.updateRD(station.Name,station.Vk)
            self.resetStation(station)
            self.takeIn = True
        elif(station.Op == "RET"):
            self.goState(station.Vj)
            self.resetStation(station)
            self.takeIn = True
        self.registerFile.setRegisterVal("R0",0)

    def finishStation(self,finishStation:Reservation_Station):
        self.finished+=1
        self.handleOp(finishStation)

    def checkLoadDep(self,finishStation:Reservation_Station):
        finish = True
        for dep in self.StoreLoadPriority:
            name, a, _ = dep
            if "Load" in name:
                if finishStation.Name == name:
                    currindex = self.StoreLoadPriority.index(dep)
                    address = a
        for dep in self.StoreLoadPriority:
            name, a, calc= dep
            if "Store" in name:
                if finishStation.Name != name and self.StoreLoadPriority.index(dep)<currindex and a == address and calc == 1:
                    finish = False
                elif self.StoreLoadPriority.index(dep)<currindex and calc ==0: #at least one station that is before in the queue didnt calculate address so we still dont know where to finish
                    finish = False
        if finish:
            del self.StoreLoadPriority[currindex]
            self.finishStation(finishStation)


    def checkStoreDep(self,finishStation:Reservation_Station):
        finish = True
        for dep in self.StoreLoadPriority:
            name, a, _ = dep
            if "Store" in name:
                if finishStation.Name == name:
                    currindex = self.StoreLoadPriority.index(dep)
                    address = a
        for dep in self.StoreLoadPriority:
            name, a, calc = dep
            if "Load" in name or "Store" in name:
                if finishStation.Name != name and self.StoreLoadPriority.index(dep)<currindex and a == address and calc == 1:
                    finish = False
                elif self.StoreLoadPriority.index(dep)<currindex and calc ==0: #at least one station that is before in the queue didnt calculate address so we still dont know where to finish
                    finish = False
        if finish:
            self.finishStation(finishStation)
            del self.StoreLoadPriority[currindex]

    def updateRunning(self):
        for station in self.Reservation_Stations:
            if station.currCycle >= station.maxCycle: #we do greater than because the cycles of the station keeps increasing when its waiting on dependencies in load / store
                if(station.Op != "LOAD"  and station.Op != "STORE"):
                    self.finishStation(station)
                elif(station.Op == "LOAD"):
                    self.checkLoadDep(station)
                elif(station.Op == "STORE"):
                    self.checkStoreDep(station)
            elif station.currCycle ==1 and station.Op == "STORE" or station.Op == "LOAD": #calculate address
                self.handleOp(station)
        for station in self.Reservation_Stations:
            if station.Qj == "" and station.Qk == "" and station.Busy ==1 and station.waitBranch == 0:
                station.currCycle+=1




    def startCycle(self):
        self.Clock+=1
        self.updateRunning()
        if self.takeIn: #due to jal we dont want to fetch because no matter what we need to wait for jal/ret so we can go there then execute no need to fetch

            currInst = self.readNext()
            if(currInst!=None):
                parts = currInst.split()
            else:
                return
            instruction = parts[0]
            if(currInst == "RET"):
                currStation = self.checkStation("JAL")
                if currStation!= None:
                    self.setVQ(currStation,"R1")
                    currStation.setValues(Busy=1,Op="RET")
                    self.takeIn = False
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "LOAD":
                currStation = self.checkStation("LOAD")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    offset = parts[2].split('(')[0]
                    src = parts[2].split('(')[1].rstrip(')')
                    self.setVQ(currStation,src)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Busy=1, A=offset)
                    self.StoreLoadPriority.append((currStation.Name, 0, 0))
                else:
                    self.instructions.append(currInst)
                    self.pc-=1
            elif instruction == "ADD":
                currStation = self.checkStation("ADD")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    rs1 = parts[2].replace(',', '')
                    rs2 = parts[3]
                    self.setVQ(currStation,rs1,rs2)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Busy=1)
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "ADDI":
                currStation = self.checkStation("ADD")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    rs1 = parts[2].replace(',', '')
                    imm = parts[3]
                    self.setVQ(currStation,rs1)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Op ="ADDI", Busy=1,A=imm)
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "NEG":
                currStation = self.checkStation("NEG")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    rs1 = parts[2]
                    self.setVQ(currStation,rs1)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Busy=1)
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "NAND":
                currStation = self.checkStation("NAND")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    rs1 = parts[2].replace(',', '')
                    rs2 = parts[3]
                    self.setVQ(currStation,rs1,rs2)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Busy=1)
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "SLL":
                currStation = self.checkStation("SLL")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    rs1 = parts[2].replace(',', '')
                    rs2 = parts[3]
                    self.setVQ(currStation,rs1,rs2)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Busy=1)
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "STORE":
                currStation = self.checkStation("STORE")
                if(currStation!=None):
                    rs2 = parts[1].replace(',', '')
                    offset = parts[2].split('(')[0]
                    src = parts[2].split('(')[1].rstrip(')')
                    self.setVQ(currStation,src,rs2)
                    currStation.setValues(Busy=1, A=offset)
                    self.StoreLoadPriority.append((currStation.Name, 0, 0))
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "BNE":
                currStation = self.checkStation("BNE")
                if(currStation!=None):
                    rs1 = parts[1].replace(',', '')
                    rs2 = parts[2].replace(',', '')
                    label = self.labelMap.get(parts[3])   #we need to map the label to the index in the file
                    self.setVQ(currStation,rs1,rs2)
                    self.branchDirty =1
                    currStation.setValues(Busy=1, A=int(label))
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "JAL":
                currStation = self.checkStation("JAL")
                if currStation!= None:
                    label = self.labelMap.get(parts[1])
                    self.registerFile.setRegisterQ("R1",currStation.Name)
                    currStation.setValues(Busy=1, A = int(label),Vk = self.pc +1)
                    self.takeIn = False
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

    def goState(self,state): #go to a specific state for example if I want to go back to when the instructions were at the 0 state (we keep popping so we need to go back)
        self.pc = -1
        self.instructions = self.instructionsOrg.copy()
        for _ in range(state):
            self.readNext()
    def getPrediction(self):
        if self.fail + self.success ==0: #cant divide by 0
            return 0
        return self.fail/(self.fail + self.success) * 100
    def getIPC(self):
        if self.Clock == 0:  #cant divide by 0
            return 0
        return self.finished/self.Clock



def main():
    alg = Tomasulos_Algorithm()
    alg.readInstructionsFromFile("test.txt")
    alg.startCycle()
    alg.printStation()
    alg.startCycle()
    alg.printStation()

#main()

class EducationalWindow(tk.Tk):
    def __init__(self, reservation_stations, register_file, algorithm):
        super().__init__()

        self.reservation_stations = reservation_stations
        self.register_file = register_file
        self.algorithm = algorithm
        self.title("Learn.")

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

    def update_ipc_label(self):
        ipc = self.algorithm.getIPC()  # Replace this with the actual method to get IPC from your algorithm
        self.ipc_label.config(text=f"IPC: {ipc}")

    def update_prediction_label(self):
        prediction = self.algorithm.getPrediction()  # Replace this with the actual method to get the prediction from your algorithm
        self.prediction_label.config(text=f"Fail Percentage: {prediction}%")
# algorithm = Tomasulos_Algorithm()
# algorithm.readInstructionsFromFile("test.txt")
# window = EducationalWindow(algorithm.Reservation_Stations, algorithm.registerFile, algorithm)
# window.update_labels(algorithm.Clock)
# window.mainloop()
main()

class StartWindow:
    def __init__(self):
        super().__init__()
        self.root = Tk()
        self.root.title("Tomasulos Algorithm")
        self.root.geometry("400x400")
        self.inputfile = ""
        self.instructionLabel = ""
        self.instructionEntry = Entry(self.root)
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
        SW = StartWindow() ##?
        instructions = self.instructionEntry.get() ##The problem is instructionEntry is not defined
        # instruction_lines = instructions.split('\n')
        # for line in instruction_lines:
        #     process_instruction(line)
        self.saveInstructions(instructions)

        print("Entered instructions: ", instructions)



    def saveInstructions(self, instructions):
        file_name = "instructions.txt"
        with open(file_name, 'w') as file:
            file.write(instructions)
        print("Instructions saved to", file_name)

        algorithm = Tomasulos_Algorithm()   ##
        algorithm.readInstructionsFromFile(file_name)

    def executeWritten(self):
        code_entry = Entry(self.submitInstructions())
        code_entry.pack()

        code  = code_entry.get()
        print("Executing written code:")
        print(code)

        self.root.destroy()

    def test(self):
        fileSelectButton = Button(text = "Select the file", command =self.selectFile)
        fileSelectButton.pack()

        codeButton = Button(self.root, text = "Execute Written Code", command = self.executeWritten)
        codeButton.pack()


        fileButton = Button(self.root, text = "Execute File Code:", command =self.executeFile)
        fileButton.pack()

        submitButton = Button(self.root, text = "Submit", command = self.submitInstructions)
        submitButton.pack()

        #root = Tk()
        instructionLabel = Label(self.root, text = "Enter Instructions: ")      #
        instructionLabel.pack()     #

        self.instructionEntry = Entry(self.root)     #
        self.instructionEntry.pack()     #

        self.root.mainloop()

start = StartWindow()
start.test()

# algorithm = Tomasulos_Algorithm()
# algorithm.readInstructionsFromFile("test.txt")
# window = EducationalWindow(algorithm.Reservation_Stations, algorithm.registerFile, algorithm)
# window.update_labels(algorithm.Clock)
# window.mainloop()
