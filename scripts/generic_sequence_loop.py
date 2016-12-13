import visa
import config
import matplotlib.pyplot as plt
import acquisition.sequence as sq
import numpy as np
import dbm.db
from time import sleep
import csv
from instruments.rfsource import SMB
from instruments.rfsource import SMW
from time import gmtime, strftime

#PARAMETERS GO HERE
directory= "D:\\Data\\Fluxonium #10_python code by Jon"
id = 944
rm = visa.ResourceManager()
cavity_source = SMB(rm.open_resource(config.smb_ip))
lo_source = SMB(rm.open_resource(config.smb2_ip))
qubit_source = SMW(rm.open_resource(config.smw_ip))

cnx = dbm.db.open_readonly_connection()
cursor = cnx.cursor()
dict = dbm.db.get_row(cursor, "generic_sequence", str(id))
cavity_source.set_freq(float(dict["cavity_frequency"]) / 1e9)
cavity_source.set_power(float(dict["cavity_power"]))
cavity_source.set_iq(True)
cavity_source.enable(True)
lo_source.set_freq((float(dict["cavity_frequency"]) + float(dict["if_frequency"])) / 1e9)
lo_source.set_power(16)
lo_source.set_iq(False)
lo_source.enable(True)
qubit_source.set_freq(float(dict["qubit_frequency"]) / 1e9)
qubit_source.set_power(float(dict["qubit_power"]))
qubit_source.set_iq(True)
qubit_source.enable(True)

inst = rm.open_resource(config.awg2_ip)
sequence = sq.Sequence_2Channel(inst)
sequence.load_from_db(id)
i = 1
# for i in range(1, 20):
while True:
    print (i)
    print (strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    sequence.start()
    time, mag, phase = sequence.acquire()
    # plt.plot(time,phase*180/np.pi)
    name = "\\" + dict["pulse_type"] + "_" + dict["qubit_frequency"] + "_" + str(id)
    np.savetxt(directory + name + "_time" + str(i) + ".csv", time)
    np.savetxt(directory + name + "_mag" + str(i) + ".csv", mag)
    np.savetxt(directory + name + "_phase" + str(i) + ".csv", phase)
    i = i + 1
    # sleep(10)

plt.show()
