# import tkinter
from Classes import Reservation_Station, Register_File, twos_complement


class Tomasulos_Algorithm:
    def __init__(self):
        self.Reservation_Stations = [ #creating stations required
            Reservation_Station("Load1", "LOAD",2), Reservation_Station("Load2", "LOAD",2),
            Reservation_Station("Store1", "STORE",2),Reservation_Station("Store2", "STORE",2),
            Reservation_Station("Bne1", "BNE",1),
            Reservation_Station("Jal1", "JAL",1),
            Reservation_Station("Add1", "ADD",2), Reservation_Station("Add2", "ADD"),Reservation_Station("Add3", "ADD"),
            Reservation_Station("Neg1", "NEG",2),
            Reservation_Station("Nand1", "NAND",1),
            Reservation_Station("Ssl1", "SSL",8)
            ]
        self.registerFile= Register_File()
        self.Clock = 0
        self.instructions = []
        self.Memory = {}
        self.instructionsOrg = self.instructions #used to store the instructions since we will be popping and we need the original incase of branching and jumping
        self.labelMap = {} #used to map labels to index in file
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


    def readNext(self):
        if self.instructions:
            return self.instructions.pop(0) #simply pop the last instruction, since we will store it in a var in start cycle we wont lose it
        else:
            return None #in this case we know theres nothing left to read useful for termination
    def checkStation(self,op):
        for station in self.Reservation_Stations:
            if op == station.Op and station.Busy ==0:
                return station
        return None
    def printStation(self):
        for station in self.Reservation_Stations:
            print(station.Name + ' ' + str(station.Vj) + ' ' + station.Qj + ' ' + str(station.Vk) + ' ' + (station.Qk))

    def setVQ(self,station:Reservation_Station,*args): #we assume the arguments are put in order so j then k
        index = 0
        for argument in args:
            if self.registerFile.getRegisterQ(argument) != "":
                if index ==0:
                    station.setValues(Qj = argument)
                else:
                    station.setValues(Qk = argument)
            else:
                if index ==0:
                    station.setValues(Vj = self.registerFile.getRegisterVal(argument))
                else:
                    station.setValues(Vk = self.registerFile.getRegisterVal(argument))
    def updateRD(self,name,value):
        for register in self.registerFile.Registers:
            if register.Qi == name:
                register.Qi == ""
                register.Value = value
    def updateMemory(self):
        return #we will update memory here


    def handleOp(self,station:Reservation_Station):
        if(station.Op == "LOAD" and station.currCycle == station.maxCycle):
            self.updateRD(station.Name,self.Memory[station.A])
        elif(station.Op == "LOAD" and station.currCycle == 1):
            station.A = station.A + station.Vj
        elif(station.Op == "STORE" and station.currCycle == station.maxCycle):
            self.updateMemory()
        elif(station.Op == "STORE" and station.currCycle == 1):
            station.A = station.A + station.Vj
        elif(station.Op == "ADD"):
            self.updateRD(station.Name,station.Vj + station.Vk)
        elif(station.Op == "ADDI"):
            self.updateRD(station.Name,station.Vj + station.A)
        elif(station.Op == "NEG"):
            self.updateRD(station.Name,twos_complement(station.Vj,16))
        elif(station.Op == "NAND"):
            self.updateRD(station.Name,~(station.Vj &station.Vk))
        elif(station.Op == "SLL"):
            self.updateRD(station.Name,station.Vj << station.Vk)
        elif(station.Op == "BNE"):
            self.predictions+=1
            if station.Vj!= station.Vk:
                #branching logic needed for resetting affected registers
                self.goState(station.A)
                self.fail+=1
            else:
                #branching logic needed for allowing the excution of the stations that were waiting
                self.success+=1
        elif(station.Op == "JAL"):
            self.updateRD(station.Name,self.memory[station.A])

    def finishStation(self,finishStation:Reservation_Station):
        self.handleOp(station)
        for station in self.Reservation_Stations:
            if station.Qj == finishStation.Name:
                station.Qj = ""
            elif station.Qk == finishStation.Name:
                station.Qk = ""
            finishStation.Vj = 0
            finishStation.Vk = 0
            finishStation.Qj = ""
            finishStation.Qk = ""
            finishStation.Busy = 0
            finishStation.A = 0
            finishStation.currCycle=0

    def updateRunning(self):
        for station in self.Reservation_Stations:
            if station.currCycle == station.maxCycle:
                self.finishStation(station)
            elif station.currCycle ==1 and station.Op == "STORE" or station.Op == "LOAD":
                self.handleOp(station)
        for station in self.Reservation_Stations:
            if station.Qj == "" and station.Qk == "" and station.Busy ==1:
                station.currCycle+=1




    def startCycle(self):
        self.Clock+=1
        self.updateRunning()
        currInst = self.readNext()
        if(currInst!=None):
            parts = currInst.split()
        else:
            return
        instruction = parts[0]
        if(currInst == "ret"):
            currStation = self.checkStation("JAL")
            if currStation!= None:
                #leave this part to me
                #self.setVQ(currStation, "R1")
                #currStation.setValues(Busy=1, A=)
                return

        elif instruction == "LOAD":
            currStation = self.checkStation("LOAD")
            if(currStation!=None):
                rd = parts[1].replace(',', '')
                offset = parts[2].split('(')[0]
                src = parts[2].split('(')[1].rstrip(')')
                self.registerFile.setRegisterQ(rd,currStation.Name)
                self.setVQ(currStation,src)
                currStation.setValues(Busy=1, A=offset)
        elif instruction == "ADD":
            currStation = self.checkStation("ADD")
            if(currStation!=None):
                rd = parts[1].replace(',', '')
                rs = parts[2].replace(',', '')
                rt = parts[3].replace(',', '')
                self.registerFile.setRegisterQ(rd,currStation.Name)
                self.setVQ(currStation,rs,rt)
                currStation.setValues(Busy=1)

            return #you can continue here

    def goState(self,state): #go to a specific state for example if I want to go back to when the instructions were at the 0 state (we keep popping so we need to go back)
        self.instructions = self.instructionsOrg
        for _ in range(0,state):
            self.readNext()


def main():
    alg = Tomasulos_Algorithm()
    alg.registerFile.setRegisterVal("R0",1)
    alg.registerFile.setRegisterQ("R0", "ADD1")
    alg.readInstructionsFromFile("test.txt")
    alg.startCycle()
    alg.printStation()
    alg.startCycle()
    alg.printStation()

main()

# top = tkinter.Tk()
# # Code to add widgets will go here...
# top.mainloop()
