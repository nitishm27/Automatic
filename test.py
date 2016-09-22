import matplotlib.pyplot as plt
import visa
import acquisition.continuous
import acquisition.sequence
import acquisition.continuous as con
import config
from acquisition.continuous import Onetone_Frequency
from instruments.rfsource import SGMA
from instruments.rfsource import SMB
from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import numpy as np
import acquisition.util as util

# npt = NPT(atsapi.Board(systemId=1, boardId=1))
# npt.buffers_per_acquisition = 100000
# npt.records_per_buffer = 10
#
# avgd_buffer = np.zeros(npt.records_per_buffer * npt.post_trigger_samples * 2)
#
# def avg1(avg_buf, buf):
#     avg_buf += buf
#
# def proc(buf):
#     avg1(avgd_buffer, buf)
#
# npt.configure_board()
# npt.acquire_data(proc, verbose=True)
# cha = avgd_buffer[0:int(len(avgd_buffer)/2)] / npt.buffers_per_acquisition
# chb = avgd_buffer[int(len(avgd_buffer)/2):len(avgd_buffer)] / npt.buffers_per_acquisition
# mag,phase = util.iq_demod_subtract(cha, chb, npt, 50e6)
#
# plt.plot(phase)
# plt.plot(mag)
# plt.show()

# rm = visa.ResourceManager()
# inst = rm.open_resource(config.awg2_ip)
# ot = acquisition.sequence.Sequence_2Channel(inst)
# ot.load_from_db(13)
# ot.start()
# time, mag, phase = ot.acquire()
# plt.plot(time,phase)
# plt.show()
