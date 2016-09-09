class SGMA:
    def __init__(self, inst):
        self.inst = inst
        self.set_ext_clock(True)

    def enable(self, bool):
        if bool:
            self.inst.write('OUTPut 1')
        else:
            self.inst.write('OUTPut 0')

    def set_iq(self, bool):
        if bool:
            self.inst.write(':SOURce:IQ:STATe ON')
        else:
            self.inst.write(':SOURce:IQ:STATe OFF')

    def set_ext_clock(self, bool):
        if bool:
            self.inst.write(':SOURce:ROSCillator:EXTernal:FREQuency 10MHz')
            self.inst.write(':SOURce:ROSCillator:OUTput:FREQuency 10MHZ')
            self.inst.write(':SOURce:ROSCillator:SOURce EXT')
        else:
            self.inst.write(':SOURce:ROSCillator:SOURce INT')

    def set_freq(self, freq): #input frequency in GHz
        self.inst.write(':SOURce:FREQuency:CW ' + str(freq) + ' GHz')

    def get_freq(self):
        return self.inst.query(':SOURce:FREQuency:CW?')

    def set_power(self, power): #input power in dBm
        self.inst.write(':SOURce:POWer  ' + str(power) + 'dBm')

    def get_power(self):
         return float(self.inst.query(':SOURce:POWer:PEP?'))

    def reset(self):
        self.inst.write('*RST; *CLS')

class SMB:
    def __init__(self, inst):
        self.inst = inst
        self.set_ext_clock(True)

    def enable(self, bool):
        if bool:
            self.inst.write('OUTP ON')
        else:
            self.inst.write('OUTP OFF')

    def set_iq(self, bool):
        if bool:
            self.inst.write('SOUR:MOD:ALL:STAT ON')
        else:
            self.inst.write('SOUR:MOD:ALL:STAT ON')

    def set_ext_clock(self, bool):
        if bool:
            self.inst.write(':SOURce:ROSCillator:EXTernal:FREQuency 10MHz')
            self.inst.write(':SOURce:ROSCillator:SOURce EXT')
        else:
            self.inst.write(':SOURce:ROSCillator:SOURce INT')

    def set_freq(self, freq): #input frequency in GHz
        self.inst.write(':SOURce:FREQuency:CW ' + str(freq) + ' GHz')

    def get_freq(self):
        return self.inst.query(':SOURce:FREQuency:CW?')

    def set_power(self, power): #input power in dBm
        self.inst.write(':SOURce:POWer  ' + str(power) + 'dBm')

    def get_power(self):
        return float(self.inst.query(':SOURce:POWer:PEP?'))

    def reset(self):
        self.inst.write('*RST; *CLS')

class SMW:
    def __init__(self, inst):
        self.inst = inst
        self.set_ext_clock(True)

    #enables
    def enable(self, bool):
        if bool:
            self.inst.write('OUTP:ALL ON')
        else:
            self.inst.write('OUTP:ALL OFF')

    #sets iq
    def set_iq(self, bool):
        if bool:
            self.inst.write('IQ:STAT ON')
        else:
            self.inst.write('IQ:STAT OFF')

    #sets ext clock to 10 mhz
    def set_ext_clock(self, bool):
        if bool:
            self.inst.write('ROSC:EXT:FREQ 10MHZ')
            self.inst.write('ROSC:OUTP:FREQ:MODE DER10M')
            self.inst.write('ROSC:SOUR EXT')
        else:
            self.inst.write('ROSC:SOUR INT')

    #sets freq
    def set_freq(self, freq): #input frequency in GHz
        self.inst.write('FREQuency 5 GHz ' + str(freq) + ' GHz')

    #gets freq
    def get_freq(self):
        return self.inst.query(':SOURce:FREQuency?')

    #sets power
    def set_power(self, power): #input power in dBm
        self.inst.write('POW:POW ' + str(power) + 'dBm')

    #gest power
    def get_power(self):
        return float(self.inst.query('POW:POW?'))

    def reset(self):
        self.inst.write('*RST; *CLS')