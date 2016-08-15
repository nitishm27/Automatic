import acquisition.sequence_2channel as sq
import acquisition.onetone_2channel as con
import sequence.sequence
import config
import visa
import matplotlib.pyplot as plt
from rfsource import SGMA

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg_ip)
one_tone = con.Onetone_2channel(inst)
one_tone.load_from_db(1)
one_tone.start()
rf_sgma = SGMA(rm.open_resource(config.rfsource_ip))
lo_sgma = SGMA(rm.open_resource(config.rfsource2_ip))
rf_sgma.set_iq(True)
rf_sgma.enable(True)
lo_sgma.enable(True)
one_tone.acquire()
rf_sgma.enable(False)
lo_sgma.enable(False)
# rabi_sequence = sq.Sequence_2Channel(sq.Sequence_Type.rabi, inst)
# rabi_sequence.load_from_db(5)
# rabi_sequence.npt.buffers_per_acquisition = 1000
# rabi_sequence.start()
# sq = rabi_sequence.acquire()
# rabi_sequence.close()
# plt.plot(sq)
# plt.show()












