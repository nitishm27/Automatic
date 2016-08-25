import visa
import config
import matplotlib.pyplot as plt
import acquisition.sequence_2channel as sq
import numpy as np

DIRECTORY="."
ID = 3

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg_ip)
sequence = sq.Sequence_2Channel(inst)
sequence.load_from_db(ID)
sequence.npt.buffers_per_acquisition = 10
sequence.start()
time, mag, phase = sequence.acquire()

np.savetxt(DIRECTORY + "\\generic_sequence" + str(ID) + "_time.csv", time)
np.savetxt(DIRECTORY + "\\generic_sequence" + str(ID) + "_mag.csv", mag)
np.savetxt(DIRECTORY + "\\generic_sequence" + str(ID) + "_phase.csv", phase)
plt.plot(time, phase)
plt.show()
