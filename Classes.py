
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
            raise ValueError(f"Invalid register name: {alias}")
    def setRegisterVal(self, alias, value):
        index = self.registerMap.get(alias)
        if index is not None:
            self.Registers[index].Value = value
        else:
            raise ValueError(f"Invalid register name: {alias}")
    def getRegisterQ(self, alias):
        index = self.registerMap.get(alias)
        if index is not None:
            return self.Registers[index].Qi
        else:
            raise ValueError(f"Invalid register name: {alias}")
    def setRegisterQ(self, alias, Q):
        index = self.registerMap.get(alias)
        if index is not None:
            self.Registers[index].Qi = Q
        else:
            raise ValueError(f"Invalid register name: {alias}")
