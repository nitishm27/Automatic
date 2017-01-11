import pyvisa as visa
import config
import time
from instruments.hpsynth import HPSynth

rm = visa.ResourceManager()
res = rm.open_resource(config.hpsynth_gpib)
# res.control_ren(0)
hp = HPSynth(res)
hp.enable(False)
hp.set_freq(3)
res.write('K4L8')
hp.enable(True)
hp.set_ext_clock(True)
hp.set_power(-17)
hp.set_iq(False)