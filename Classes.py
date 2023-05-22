
def twos_complement(num, num_bits):
    mask = (1 << num_bits) - 1
    if num < 0:
        num = num & mask
    return num ^ mask

class Reservation_Station:
    def __init__(self, Name, Op,Cycles):
        self.Name = Name
        self.Op = Op
        self.Vj = 0
        self.Vk = 0
        self.Qj = ""
        self.Qk = ""
        self.Busy = 0
        self.A = 0
        self.maxCycle =Cycles
        self.currCycle=0
        self.waitBranch = 0

    def setValues(self, **kwargs): #easy way of setting values without making a bunch of setters
        for key, value in kwargs.items():
            setattr(self, key, value)

class Register:
    def __init__(self):
        self.Value = 0
        self.Qi = ""

class Register_File:
    def __init__(self):
        self.Registers = [Register() for _ in range(8)]
        self.registerMap = {'R0': 0,'R1': 1,'R2': 2,'R3': 3,'R4': 4,'R5': 5,'R6': 6,'R7': 7}

    def getRegisterVal(self, alias):
        index = self.registerMap.get(alias)
        if index is not None:
            return self.Registers[index].Value
        else:
            return self.Registers[0].Value #forcing it to return 0
    def setRegisterVal(self, alias, value):
        index = self.registerMap.get(alias)
        if index is not None:
            if value > 32767: #defaulting to setting max 16 bit number if its larger than the size specified
                value = 32767
            elif value < -32768:  #defaulting to setting max 16 bit number if its smaller than the size specified
                value = -32768
            self.Registers[index].Value = value
    def getRegisterQ(self, alias):
        index = self.registerMap.get(alias)
        if index is not None:
            return self.Registers[index].Qi
        else:
            return self.Registers[0].Qi
    def setRegisterQ(self, alias, Q):
        index = self.registerMap.get(alias)
        if index is not None:
            self.Registers[index].Qi = Q
