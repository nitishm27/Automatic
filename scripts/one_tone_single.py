import matplotlib.pyplot as plt
import numpy as np
import visa

import acquisition.continuous as con
import config
from acquisition.continuous import Onetone_Frequency
from instruments.rfsource import SGMA

#Not connected to the database, just for test purposes
DIRECTORY = "C:\\Users\\nguyen89\Desktop"
NAME = "test"
MEASUREMENT_ID = 2
START_FREQ = 10e9
STOP_FREQ = 11e9
STEPS = 100

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg2_ip)
one_tone = con.Continuous(inst)
one_tone.load_from_db(MEASUREMENT_ID)
# one_tone.npt.buffers_per_acquisition = 100
cavity_sgma_inst = rm.open_resource(config.smb_ip)
lo_sgma_inst = rm.open_resource(config.smb2_ip)
cavity_sgma = SGMA(cavity_sgma_inst)
lo_sgma = SGMA(lo_sgma_inst)
onetone_freq = Onetone_Frequency(inst, lo_sgma, cavity_sgma, one_tone)
onetone_freq.start()
freqs, mag, phase = onetone_freq.acquire(START_FREQ, STOP_FREQ, STEPS, verbose=True)

np.savetxt(DIRECTORY + "\\" + NAME + "_freq.csv", freqs)
np.savetxt(DIRECTORY + "\\" + NAME + "_mag.csv", mag)
np.savetxt(DIRECTORY + "\\" + NAME + "_phase.csv", phase)
plt.plot(freqs, mag)
plt.show()
plt.plot(freqs,phase)
plt.show()