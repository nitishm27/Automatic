import pulse.pulse
import config
import visa

rm = visa.ResourceManager()
awg = rm.open_resource(config.awg_ip)
t2 = pulse.pulse.T2_echo_Sequence(awg)
t2.qubit_width = 100
t2.qubit_width_pi = 200
t2.t_inc = 100
t2.num_pulses = 50
t2.samples = 30000
t2.delay_const1 = 300
t2.delay_const2 = 300
t2.cavity_width = 2000
t2.marker_width = 1000
t2.pulse_type = "gaussian"
t2.load_sequence()