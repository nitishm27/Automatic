import visa
import config
import matplotlib.pyplot as plt
import acquisition.sequence_2channel as sq
import awg

# rm = visa.ResourceManager()
# awg_inst = rm.open_resource(config.awg2_ip)
# pulse = sequence.sequence.T1_Sequence(awg_inst)
# pulse.load_from_db(2)
# pulse.load_sequence()

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg2_ip)
rabi_sequence = sq.Sequence_2Channel(sq.Sequence_Type.t1, inst)
rabi_sequence.load_from_db(3)
rabi_sequence.npt.buffers_per_acquisition = 10
rabi_sequence.start()
sq = rabi_sequence.acquire()
rabi_sequence.close()
plt.plot(sq)
plt.show()
inst.close()