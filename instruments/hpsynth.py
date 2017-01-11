import pyvisa

#THIS CLASS DOESNT 100% WORK, READ ALL THE COMMENTS

#If you dont reset the default values arent guaranteed to be correct!
class HPSynth:
    def __init__(self, inst, reset=True):
        self.inst = inst
        self.inst.control_ren(1)
        if reset:
            self.reset()
        self.ext_clock = False
        self.output = False
        self.freq = 3
        self.power = 0

    def enable(self, bool):
        self.output = bool
        self.update_output()

    def set_iq(self, bool): #warning: modulation (on state) not tested!
        if bool:
            self.inst.write('M2N6')
        else:
            self.inst.write('M0N6')

    def set_ext_clock(self, bool):
        self.ext_clock = bool
        self.update_output()

    def set_freq(self, freq): #input frequency in GHz
        self.freq = freq
        value = freq*10**6
        ref = 10**7
        Nzeros = 0
        c = value
        while c < ref:
            Nzeros = Nzeros + 1
            c = c * 10
        self.inst.write('P'+'0'*Nzeros+str(int(value))+'Z0')

    def get_freq(self): #set_freq or reset must be called for this to be accurate!
        return self.freq

    def set_power(self, power): #input power in dBm
        self.power = power
        value = power - 10
        if value > 0:
            self.inst.write('K0L'+str(int(3-value)))
        else:
            power_range = int(-value) / 10
            vernier = int(-value) % 10 + 3
            if power_range == -100:
                power_range = ':'
            elif power_range == -110:
                power_range = ';'
            if vernier > 9:
                vernier = (':',';','<')[vernier - 10]
            self.inst.write('K'+str(power_range)+'L'+str(vernier))

    def get_power(self): #set_power or reset must be called for this to be accurate!
        return self.power

    def reset(self):
        self.inst.clear()
        self.ext_clock = False
        self.output = False
        self.freq = 3
        self.power = 0
        self.update_output()

    def update_output(self):
        if self.ext_clock and self.output:
            self.inst.write('O7')
        elif self.ext_clock and not self.output:
            self.inst.write('O6')
        elif not self.ext_clock and self.output:
            self.inst.write('O3')
        else:
            self.inst.write('O2')
