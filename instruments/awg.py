import numpy as np
import struct
import binascii
from enum import Enum
import ctypes

class Runmode(Enum):
    sequence = 1
    continuous = 2

def add_waveform(waveform, name, inst, marker1=None, marker2=None):
    inst.write("WLISt:WAVeform:DELETE " + repr(name))
    inst.write("WLISt:WAVeform:NEW " + repr(name) + "," + str(len(waveform)) + ",REAL")
    inst.values_format.use_binary('f', False, np.array)
    bytes = [None] * len(waveform)
    marker1_true = np.any(marker1)
    marker2_true = np.any(marker2)
    for i, f in enumerate(waveform):
        marker_byte = 0
        if marker1_true and marker1[i] != 0:
            marker_byte += 64
        if marker2_true and marker2[i] != 0:
            marker_byte += 128
        marker_str = chr(marker_byte).encode()
        bytes[i] = float_to_bitstring(f) + marker_str
    byte_str = b''.join([byte for byte in bytes])
    num_bytes = len(waveform) * 5
    digits = int(np.floor(np.log10(num_bytes) + 1))
    bytes = b'#' + str(digits).encode() + str(num_bytes).encode() + byte_str
    command = b'WLISt:WAVeform:DATA \"' + name.encode() + b'\",0,' + str(len(waveform)).encode() + b',' + bytes
    inst.write_raw(command)

def clear_sequence(inst):
    inst.write("SEQuence:LENGth 0")

def add_to_sequence(channel, name, position, inst):
    current_length = int(inst.query("SEQuence:LENGth?"))
    if position > current_length:
        inst.write("SEQuence:LENGth " + str(position))
    inst.write("SEQuence:ELEMent" + str(position) + ":WAVeform" + str(channel) + " " + repr(name))

def add_to_continuous(channel, name, inst):
    inst.write("SOURCE" + str(channel) + ":WAVEFORM" + " "  + repr(name) )

def set_repeat(position, repeat, inst):
    inst.write('SEQUENCE:ELEMENT' + str(position) + ':LOOP:COUNT ' + str(repeat))

def set_goto(position, goto, inst):
    inst.write('SEQuence:ELEMent' + str(position) + ':GOTO:STATe 1')
    inst.write('SEQuence:ELEMent' + str(position) + ':GOTO:INDex ' + str(goto))

def start(inst):
    inst.write("OUTPUT1:STATE ON")
    inst.write("OUTPUT2:STATE ON")
    inst.write("AWGCONTROL:RUN")

def set_mode(mode, inst):
    if mode == Runmode.sequence:
        inst.write("AWGCONTROL:RMODE SEQuence")
    elif mode == Runmode.continuous:
        inst.write("AWGCONTROL:RMODE CONTINUOUS")

def set_ref_clock(bool, inst):
    if (bool):
        inst.write('SOURCE1:ROSCILLATOR:SOURCE EXTERNAL')
    else:
        inst.write('SOURCE1:ROSCILLATOR:SOURCE INTERNAL')

#sets in MHz
def set_ref_freq(freq, inst):
    inst.write("SOURCE1:ROSCILLATOR:FREQUENCY " + str(freq) +"MHZ")

def stop(inst):
    inst.write("AWGCONTROL:STOP")

def float_to_bitstring(f):
    float_pointer = ctypes.pointer(ctypes.c_float(f))
    char_pointer = ctypes.cast(float_pointer, ctypes.POINTER(ctypes.c_char * 4))
    return b''.join([byte for byte in char_pointer.contents])