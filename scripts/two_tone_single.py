import matplotlib.pyplot as plt
import numpy as np
import visa

import acquisition.continuous as con
import config
from acquisition.continuous import Twotone_Frequency
from instruments.rfsource import SGMA

#Not connected to the database, just for test purposes
DIRECTORY = "C:\\Users\\nguyen89\Desktop"
NAME = "test"
PULSE_ID = 2
START_FREQ = 10.29e9
STOP_FREQ = 10.31e9
CAV_FREQ = 10.304e9
IF_FREQ = 5e7
STEPS = 50

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg2_ip)
one_tone = con.Continuous(inst)
one_tone.load_from_db(PULSE_ID)
# one_tone.npt.buffers_per_acquisition = 100
cavity_sgma_inst = rm.open_resource(config.smb_ip)
lo_sgma_inst = rm.open_resource(config.smb2_ip)
cavity_sgma = SGMA(cavity_sgma_inst)
lo_sgma = SGMA(lo_sgma_inst)
cavity_sgma.set_iq(True)
lo_sgma.set_iq(False)
cavity_sgma.set_ext_clock(True)
lo_sgma.set_ext_clock(True)
cavity_sgma.set_freq(CAV_FREQ / 1e9)
lo_sgma.set_freq((CAV_FREQ + IF_FREQ) / 1e9)
cavity_sgma.enable(True)
lo_sgma.enable(True)

twotone_freq = Twotone_Frequency(inst, lo_sgma, cavity_sgma, one_tone)
twotone_freq.start()
freqs, mag, phase = twotone_freq.acquire(START_FREQ, STOP_FREQ, STEPS, verbose=True)

np.savetxt(DIRECTORY + "\\" + NAME + "_freq.csv", freqs)
np.savetxt(DIRECTORY + "\\" + NAME + "_mag.csv", mag)
np.savetxt(DIRECTORY + "\\" + NAME + "_phase.csv", phase)
plt.plot(freqs, mag)
plt.show()
plt.plot(freqs,phase)
plt.show()