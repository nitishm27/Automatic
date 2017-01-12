from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

npt = NPT(atsapi.Board(systemId=1, boardId=1))
npt.post_trigger_samples = 1024
npt.records_per_buffer = 100
npt.samples_per_sec = 1e9
if_freq = 5e7
rel_phase = np.pi / 2

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
    xdata = np.linspace(0,period-1,period)
    def wave(t, a, phase):
        return a*np.sin(2*np.pi * t / period + phase)
    mag = np.zeros(npt.records_per_buffer)
    phase = np.zeros(npt.records_per_buffer)
    for i in range(npt.records_per_buffer):
        num_periods = int(npt.post_trigger_samples / period)
        record_mag = np.zeros(num_periods)
        record_phase = np.zeros(num_periods)
        for j in range(num_periods):
            ch1_period = ch1[i*npt.post_trigger_samples + j*period:i*npt.post_trigger_samples+(j+1)*period]
            ch2_period = ch2[i*npt.post_trigger_samples + j*period:i*npt.post_trigger_samples+(j+1)*period]
            ch1_opt = fit_single_period(xdata, wave, ch1_period, npt)
            ch2_opt = fit_single_period(xdata, wave, ch2_period, npt)
            record_mag[j] = ch1_opt[0]
            record_phase[j] = ch1_opt[1] - ch2_opt[1]
        mag[i] = np.mean(record_mag)
        phase[i] = np.mean(np.unwrap(record_phase))
    return mag, np.unwrap(phase)

def fit_single_period(xdata, wave, ydata, npt):
    peak = max(ydata)
    guess = [peak, np.arcsin(ydata[0]/peak)]
    return curve_fit(wave, xdata, ydata, guess)[0]

ch1, ch2 = gen_fake_data(npt, if_freq, rel_phase)
mag, phase = fit_demod(ch1, ch2, npt, if_freq)

plt.plot(mag)
plt.plot(phase)
plt.show()
