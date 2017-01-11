#NOT IMPLEMENTED
class Yokogawa:
    def __init__ (self, inst):
        self.inst = inst

    def enable(self, bool):
        if bool:
            self.inst.write('O1')
        else:
            self.inst.write('O0')

    def get_current(self):
        return None

    def set_current(self, current, steps):
        return None

    def get_voltage(self):
        return None

    def set_voltage(self):
        return None

    def set_mode(self, mode):
        if mode:
            self.inst.write('F1')
        else:
            self.inst.write('F2')
        return None

    def set_range(self, range):
        return None




