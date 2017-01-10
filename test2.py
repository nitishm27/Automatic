import pyvisa as visa
import config
import time
from instruments.hpsynth import HPSynth

rm = visa.ResourceManager()
res = rm.open_resource(config.hpsynth_gpib)
# res.write_raw(b'x07')
# visa_library = visa.highlevel.VisaLibrary()
# res.write('RL2')
res.control_ren(0)
# res.control_atn(0)
res.write('K1L7')
# hpsynth = HPSynth(res)
# # hpsynth.set_ext_clock(True)
# # hpsynth.enable(True)
# hpsynth.set_power(10)
# hpsynth.enable(True)