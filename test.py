# import pulse.pulse
# from pulse import functions
# import config
# import visa
from matplotlib import pyplot as plt
import numpy as np
# rm = visa.ResourceManager()
# awg = rm.open_resource(config.awg_ip)
# t2 = pulse.pulse.T2_echo_Sequence(awg)
# t2.qubit_width = 100
# t2.qubit_width_pi = 200
# t2.t_inc = 100
# t2.num_pulses = 50
# t2.samples = 30000
# t2.delay_const1 = 300
# t2.delay_const2 = 300
# t2.cavity_width = 2000
# t2.marker_width = 1000
# t2.pulse_type = "gaussian"
# t2.load_sequence()

edge_width = 200
pulse_width = 20000

empty_arr = np.zeros(pulse_width)
pulse = np.ones(pulse_width)
x = np.linspace(0,4*edge_width,4*edge_width)
gaussian_arr = np.power(2, -1 * np.power(2*(x - 2*edge_width)/edge_width, 2))
pulse[-1*(2*edge_width)::] = gaussian_arr[-1*(2*edge_width)::]
pulse[0:2*edge_width]=gaussian_arr[0:2*edge_width]
plt.plot(pulse)
plt.show()