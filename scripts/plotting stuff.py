import numpy as np
from matplotlib import pyplot as plt

path = "D:\Data\Fluxonium #10_New software\Two tone spec_YOKO0mA_1mA_Qubit9p3 to 9p5GHz n30dBm_Cav 10p313GHz 1dBm_test.dat"

data = np.genfromtxt(path)
# current = data[1::,0]
current = np.linspace(0,1,11)
# freq = data[1::,1]
phase = data[1::,2]
freq_num = 201
freq = np.linspace(9.3, 9.5, freq_num)
phase_ma = np.zeros((len(current),freq_num))
for idx in range (11):
    phase_ma[idx] = np.unwrap(phase[idx*freq_num:idx*freq_num + freq_num])

X,Y = np.meshgrid(current, freq)
Z=phase_ma.transpose()

plt.pcolormesh(X,Y,Z, cmap = 'GnBu', vmin = -3, vmax =1)

plt.show()


