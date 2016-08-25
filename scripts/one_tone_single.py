import acquisition.onetone_2channel as con
import config
import visa
import matplotlib.pyplot as plt
from rfsource import SGMA
from acquisition.onetone_2channel import Onetone_Frequency
import numpy as np

#Not connected to the database, just for test purposes
DIRECTORY = "."
NAME = "test"
PULSE_ID = 1
START_FREQ = 10e9
STOP_FREQ = 11.8e9
STEPS = 10

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg_ip)
one_tone = con.Onetone_2channel(inst)
one_tone.load_from_db(PULSE_ID)
rf_sgma_inst = rm.open_resource(config.rfsource_ip)
lo_sgma_inst = rm.open_resource(config.rfsource2_ip)
rf_sgma = SGMA(rf_sgma_inst)
lo_sgma = SGMA(lo_sgma_inst)
onetone_freq = Onetone_Frequency(inst, lo_sgma, rf_sgma, one_tone)
onetone_freq.start()
freqs, mag, phase = onetone_freq.acquire(START_FREQ, STOP_FREQ, STEPS, verbose=True)

np.savetxt(DIRECTORY + "\\" + NAME + "_freq.csv", freqs)
np.savetxt(DIRECTORY + "\\" + NAME + "_mag.csv", mag)
np.savetxt(DIRECTORY + "\\" + NAME + "_phase.csv", phase)
plt.plot(freqs, phase)
plt.show()