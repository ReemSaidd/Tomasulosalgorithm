from Classes import Reservation_Station, Register_File
from tkinter import Tk, Button, Entry, filedialog, Label, Text
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
        self.status = []
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
                value = int(newline[1])
                if value < -32768:
                    value = -32768
                if value > 32767:
                    value = 32767
                self.Memory[int(newline[0])] = value
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

    def showMemory(self):
        return self.Memory
    def showStatus(self):
        return self.status
    
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
        for x in self.status:
            if x[1] == finishStation.Name and x[6] == "":
                x[6] = self.Clock - 1
                x[5] = self.Clock - 2

            
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
            if station.currCycle ==1:
                for x in self.status:
                    if x[1] == station.Name and x[3]== "":
                        x[3] = self.Clock-1
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "LOAD":
                currStation = self.checkStation("LOAD")
                if(currStation!=None):
                    rd = parts[1].replace(',', '')
                    offset = parts[2].split('(')[0]
                    if(int(offset)>64):
                        offset = 64
                    if(int(offset)<-63):
                        offset = -63
                    src = parts[2].split('(')[1].rstrip(')')
                    self.setVQ(currStation,src)
                    self.registerFile.setRegisterQ(rd,currStation.Name)
                    currStation.setValues(Busy=1, A=offset)
                    self.StoreLoadPriority.append((currStation.Name, 0, 0))
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
                else:
                    self.instructions.append(currInst)
                    self.pc-=1

            elif instruction == "STORE":
                currStation = self.checkStation("STORE")
                if(currStation!=None):
                    rs2 = parts[1].replace(',', '')
                    offset = parts[2].split('(')[0]
                    if(int(offset)>64):
                        offset = 64
                    if(int(offset)<-63):
                        offset = -63
                    src = parts[2].split('(')[1].rstrip(')')
                    self.setVQ(currStation,src,rs2)
                    currStation.setValues(Busy=1, A=offset)
                    self.StoreLoadPriority.append((currStation.Name, 0, 0))
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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
                    self.status.append(currInst,currStation.Name, self.Clock, "" ,"", "", "")
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

#main()

# algorithm = Tomasulos_Algorithm()
# algorithm.readInstructionsFromFile("test.txt")
# window = EducationalWindow(algorithm.Reservation_Stations, algorithm.registerFile, algorithm)
# window.update_labels(algorithm.Clock)
# window.mainloop()


# algorithm = Tomasulos_Algorithm()
# algorithm.readInstructionsFromFile("test.txt")
# window = EducationalWindow(algorithm.Reservation_Stations, algorithm.registerFile, algorithm)
# window.update_labels(algorithm.Clock)
# window.mainloop()
