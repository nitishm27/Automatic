import acquisition.sequence_2channel as sq
import acquisition.onetone_2channel as con
import sequence.sequence
import config
import visa
import matplotlib.pyplot as plt
from rfsource import SGMA
import numpy as np
import awg
import ctypes

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg_ip)
one_tone = con.Onetone_2channel(inst)
one_tone.load_from_db(1)
one_tone.npt.buffers_per_acquisition = 2000
one_tone.start()
rf_sgma_inst = rm.open_resource(config.rfsource_ip)
lo_sgma_inst = rm.open_resource(config.rfsource2_ip)
rf_sgma = SGMA(rf_sgma_inst)
lo_sgma = SGMA(lo_sgma_inst)
t = np.linspace(0,np.pi * 2,100, endpoint=False)
print(t)
sinwave = np.sin(t)
marker = np.zeros(len(sinwave))
marker[0] = 1
awg.add_waveform(sinwave, "sinewa", inst, marker1 = marker)

# flt = ctypes.c_float(-1.5)
# pointer = ctypes.pointer(flt)
# pointer2 = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_char * 4))
# arr = pointer2.contents
# for i in arr:
#     print(i)

# rf_sgma.set_iq(True)
# rf_sgma.set_ext_clock(True)
# lo_sgma.set_ext_clock(True)
# rf_sgma.enable(True)
# lo_sgma.enable(True)
#
# start_freq = 10.0
# end_freq = 12.0
# if_freq = .05
# steps = 15
# one_tones = []
#
# for freq in np.linspace(start_freq, end_freq, steps):
#     rf_sgma.set_freq(freq)
#     lo_sgma.set_freq(freq + if_freq)
#     print(rf_sgma.get_freq())
#     print(lo_sgma.get_freq())
#     one_tones.append(one_tone.acquire())
#
# plt.plot(one_tones)
# plt.show()
# rf_sgma.enable(False)
# lo_sgma.enable(False)












