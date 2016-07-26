import binascii
import struct
import visa
import config
import awg
import time
import threading
import sequence.functions
import sequence.sequence
import rfsource
from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import numpy as np
import matplotlib.pyplot as plt
rm = visa.ResourceManager()
# for resource in rm.list_resources():
#     try:
#         inst = rm.open_resource(resource)
#         print(inst.query("*IDN?"))
#         print(resource)
#         inst.close()
#     except Exception :
#         print('error')
# inst = rm.open_resource(config.rfsource_ip)
# rfsource.reset(inst)
# #inst.write(':SOURce:OPMode NORMal')
# rfsource.set_freq(0.001, inst)
# #inst.write(':SOURce:FREQuency:CW 0.01 GHz')
# #inst.write(':SOURce:POWer -10dBm')
# rfsource.set_power(-20, inst)
# #print(inst.query(':SOURce:POWer:PEP?'))
# print(rfsource.get_power(inst))
# rfsource.enable(True, inst)
# # print(inst.query("*IDN?"))
# board = atsapi.Board(systemId=1, boardId=1)
# npt = NPT(board)
# npt.recordsPerBuffer = 5
# npt.postTriggerSamples = 1024
# npt.buffersPerAcquisition = 50
# avgd_buffer = np.zeros(npt.postTriggerSamples * npt.recordsPerBuffer * 2)
#
# def test_proc(avgd, buffer):
#     avgd += buffer
#
#
# def avg(buffer):
#     test_proc(avgd_buffer, buffer)
#
# npt.acquire_data(avg, verbose=True)
# plt.plot(avgd_buffer / npt.buffersPerAcquisition)
# plt.show()

# def output_state(inst, channel, state):
#     #OUTPUT1:STATE ON
#     inst.write('OUTPUT1:STATE ON')

# wave, empty = sequence.functions.gen_gaussian(200)
# marker = np.zeros(len(wave))
# marker[0:200] = 1
# marker2 = np.zeros(len(wave))
# marker2[0:400] = 1
# awg.add_waveform(wave, "test4", inst, marker1=marker, marker2=marker2)
# print(inst.query('WLISt:WAVeform:TSTAMP? \"hjg\"'))
# inst.write("WLISt:WAVeform:DELe
# te \"asdf\"")
# inst.write_raw(b'WLIST:WAVeform:DATA? \"*Square10\",0,10')
# print(inst.read_raw())

# rm = visa.ResourceManager()
board = atsapi.Board(systemId=1, boardId=1)
npt = NPT(board)
npt.records_per_buffer = 20
npt.post_trigger_samples = 1024
npt.buffers_per_acquisition = 10
avgd_buffer = np.zeros(npt.post_trigger_samples * npt.records_per_buffer * 2)
def test_proc(avgd, buffer):
    avgd += buffer
def avg(buffer):
    test_proc(avgd_buffer, buffer)
def run_acquisition():
    npt.acquire_data(avg, verbose=True)

inst = rm.open_resource(config.awg_ip)
t1 = sequence.sequence.T1_Sequence(inst)
t1.load_from_db(33)
t1.load_sequence()
thread = threading.Thread(target=run_acquisition, args=())
thread.start()
time.sleep(.1)
awg.start(inst)
thread.join()
awg.stop(inst)
inst.close()

plt.plot(avgd_buffer / npt.buffers_per_acquisition)
plt.show()