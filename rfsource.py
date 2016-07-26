normal = 'Normal'
def enable(bool, inst):
    if bool:
        inst.write('OUTPut 1')
    else:
        inst.write('OUTPut 0')


def set_freq(freq, inst): #input frequency in GHz
    inst.write(':SOURce:FREQuency:CW ' + str(freq) + ' GHz')

def set_power(power, inst): #input power in dBm
    inst.write(':SOURce:POWer  ' + str(power) + 'dBm')

def get_power(inst):
     return float(inst.query(':SOURce:POWer:PEP?'))

def reset(inst):
    inst.write('*RST; *CLS')
