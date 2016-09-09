import visa
import config
import matplotlib.pyplot as plt
import acquisition.sequence as sq
import numpy as np
import dbm.db
import csv
from instruments.rfsource import SGMA

#PARAMETERS GO HERE
directory= "C:\\Users\\nguyen89\\Desktop"
id = 5
rm = visa.ResourceManager()
# cavity_source = SGMA(rm.open_resource(config.sgma_ip))
# lo_source = SGMA(rm.open_resource(config.sgma2_ip))
# qubit_source = SGMA(rm.open_resource(config.sgma3_ip))

cnx = dbm.db.open_readonly_connection()
cursor = cnx.cursor()
dict = dbm.db.get_row(cursor, "generic_sequence", str(id))
# cavity_source.set_freq(float(dict["cavity_frequency"]) / 1e9)
# cavity_source.set_power(float(dict["cavity_power"]))
# cavity_source.set_iq(True)
# cavity_source.enable(True)
# lo_source.set_freq((float(dict["cavity_frequency"]) + float(dict["if_frequency"])) / 1e9)
# lo_source.set_power(10)
# lo_source.set_iq(False)
# lo_source.enable(True)
# qubit_source.set_freq(float(dict["qubit_frequency"]) / 1e9)
# qubit_source.set_power(float(dict["qubit_power"]))
# qubit_source.set_iq(True)
# qubit_source.enable(True)

inst = rm.open_resource(config.awg2_ip)
sequence = sq.Sequence_2Channel(inst)
sequence.load_from_db(id)
sequence.start()
time, mag, phase = sequence.acquire()

np.savetxt(directory + "\\generic_sequence_" + str(id) + "_time.csv", time)
np.savetxt(directory + "\\generic_sequence_" + str(id) + "_mag.csv", mag)
np.savetxt(directory + "\\generic_sequence_" + str(id) + "_phase.csv", phase)
plt.plot(time, phase)
plt.show()
