import acquisition.sequence_2channel as sq
import acquisition.onetone_2channel as con
import sequence.sequence
import config
import visa
import matplotlib.pyplot as plt

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg_ip)
rabi_sequence = sq.Sequence_2Channel(sq.Sequence_Type.rabi, inst)
rabi_sequence.load_from_db(2)
rabi_sequence.npt.buffers_per_acquisition = 1000
rabi_sequence.start()
sq = rabi_sequence.acquire()
rabi_sequence.close()
plt.plot(sq)
plt.show()












