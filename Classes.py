class Reservation_Station:
    def __init__(self, Name, Op):   #Vj, Vk, Qj, Qk, Busy, A
        self.Name = Name  # Name of the reservation station
        self.Op = Op  # Operation to perform
        self.Vj = 0  # Value of operand j
        self.Vk = 0  # Value of operand k
        self.Qj = ""  # Reservation station producing Vj
        self.Qk = ""  # Reservation station producing Vk
        self.Busy = 0  # Flag indicating if the reservation station is busy
        self.A = 0  # Address for load or store operations

class Register:
    def __init__(self):  #Value, Qi
        self.Value = 0  # Value of the register
        self.Qi = ""  # Reservation station producing the value

class Register_File:
    def __init__(self):
        self.Register = [Register() for i in range(8)]  # Array of registers
