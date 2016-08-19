import acquisition.onetone_2channel as con
import config
import visa
import matplotlib.pyplot as plt
from rfsource import SGMA
from acquisition.onetone_2channel import Onetone_Frequency

rm = visa.ResourceManager()
inst = rm.open_resource(config.awg_ip)
one_tone = con.Onetone_2channel(inst)
one_tone.load_from_db(1)
one_tone.npt.buffers_per_acquisition = 1000
rf_sgma_inst = rm.open_resource(config.rfsource_ip)
lo_sgma_inst = rm.open_resource(config.rfsource2_ip)
rf_sgma = SGMA(rf_sgma_inst)
lo_sgma = SGMA(lo_sgma_inst)
onetone_freq = Onetone_Frequency(inst, lo_sgma, rf_sgma, one_tone)
onetone_freq.start()
start_freq = 10e9
end_freq = 11.8e9
steps = 180
freqs, mag, phase = onetone_freq.acquire(start_freq, end_freq, steps)
plt.plot(freqs, mag)
plt.show()












