from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import acquisition.util

npt = NPT(atsapi.Board(systemId=1, boardId=1))
npt.post_trigger_samples = 32
npt.records_per_buffer = 100
npt.samples_per_sec = .25e9
if_freq = 5e7
rel_phase = np.pi / 2
noiselevel = .02

def gen_fake_data(npt, if_freq, rel_phase):
    ch1 = np.zeros(npt.post_trigger_samples * npt.records_per_buffer)
    ch2 = np.zeros(npt.post_trigger_samples * npt.records_per_buffer)
    freq = if_freq / npt.samples_per_sec
    ch1_piece = [np.sin(2*np.pi*freq*i) for i in range(npt.post_trigger_samples)]
    ch2_piece = [np.sin(2*np.pi*freq*i + rel_phase) for i in range(npt.post_trigger_samples)]
    for i in range(npt.records_per_buffer):
        ch1[npt.post_trigger_samples * i:npt.post_trigger_samples * (i + 1)] = ch1_piece
        ch2[npt.post_trigger_samples * i:npt.post_trigger_samples * (i + 1)] = ch2_piece
    return ch1, ch2

def fit_demod(ch1, ch2, npt, if_freq):
    period = int(np.round(npt.samples_per_sec / if_freq))
    xdata = np.linspace(0,npt.post_trigger_samples-1,npt.post_trigger_samples)
    def wave(t, a, phase):
        return a*np.sin(2*np.pi * t / period + phase)
    mag = np.zeros(npt.records_per_buffer)
    phase = np.zeros(npt.records_per_buffer)
    for i in range(npt.records_per_buffer):
        ch1_opt = fit_single(xdata, wave, ch1[i*npt.post_trigger_samples:(i+1)*npt.post_trigger_samples], npt)
        ch2_opt = fit_single(xdata, wave, ch2[i*npt.post_trigger_samples:(i+1)*npt.post_trigger_samples], npt)
        mag[i]=ch1_opt[0]
        phase[i]=ch1_opt[1]-ch2_opt[1]
    return mag, np.unwrap(phase)

def fit_single(xdata, wave, ydata, npt):
    peak = max(ydata)
    guess = [peak, np.arcsin(ydata[0]/peak)]
    return curve_fit(wave, xdata, ydata, guess, maxfev=2000)[0]

min_samples = 4
max_samples = 40
sample_time = 1e-6

perror_old = []
perror_fit = []
for i in range(min_samples, max_samples):
    npt.samples_per_sec = i * if_freq
    npt.post_trigger_samples = int(sample_time * npt.samples_per_sec)
    print(npt.post_trigger_samples * if_freq / npt.samples_per_sec)
    ch1, ch2 = gen_fake_data(npt, if_freq, rel_phase)
    ch1 += np.random.normal(0,noiselevel,len(ch1))
    ch2 += np.random.normal(0,noiselevel,len(ch2))
    phase = fit_demod(ch1, ch2, npt, if_freq)[1]
    phase_old = acquisition.util.iq_demod_subtract(ch1, ch2, npt, if_freq)[1]
    perror_fit.append(np.std(phase))
    perror_old.append(np.std(phase_old))

plt.plot(perror_fit)
plt.plot(perror_old)
plt.show()
