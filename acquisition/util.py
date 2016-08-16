import numpy as np
import threading
import time
import awg
import matplotlib.pyplot as plt

def average_buffers(awg_inst, npt):
    avgd_buffer = np.zeros(npt.post_trigger_samples * npt.records_per_buffer * 2)

    def test_proc(avgd, buffer):
        avgd += buffer

    def avg(buffer):
        test_proc(avgd_buffer, buffer)

    def run_acquisition():
        npt.acquire_data(avg)

    thread = threading.Thread(target=run_acquisition, args=())
    thread.start()
    time.sleep(.1)
    awg.set_ref_clock(True, awg_inst)
    awg.set_ref_freq(10, awg_inst)
    awg.start(awg_inst)
    thread.join()
    awg.stop(awg_inst)
    ch1 = avgd_buffer[0:int(len(avgd_buffer)/2)] / npt.buffers_per_acquisition
    ch2 = avgd_buffer[int(len(avgd_buffer)/2):len(avgd_buffer)] / npt.buffers_per_acquisition
    plt.plot(ch1)
    plt.show()
    plt.plot(ch2)
    plt.show()
    return ch1, ch2

def iq_demod_subtract(ch1, ch2, npt, if_freq):
    ch1_i, ch1_q = iq_demod(ch1, npt, if_freq)
    ch2_i, ch2_q = iq_demod(ch2, npt, if_freq)
    x = ch1_i*ch2_i + ch1_q*ch2_q
    y = ch1_i*ch2_q - ch1_q*ch2_i
    phase = np.arctan2(y, x)
    return phase

def iq_demod(data, npt, if_freq):
    period_length = int(npt.samples_per_sec / if_freq)
    sine_samples = [np.sin(2*np.pi*i/period_length) for i in range(0,period_length)]
    cosine_samples = [np.cos(2*np.pi*i/period_length) for i in range(0,period_length)]
    i_values = np.zeros(npt.records_per_buffer)
    q_values = np.zeros(npt.records_per_buffer)
    dt = 1.0 / npt.samples_per_sec
    iq_per_record = int(npt.post_trigger_samples / period_length)
    for i in range(0, npt.records_per_buffer):
        avg_i = 0
        avg_q = 0
        for j in range(0, iq_per_record):
            start = i * npt.post_trigger_samples + j * period_length
            end = i * npt.post_trigger_samples + (j+1) * period_length
            avg_i = avg_i + np.sum(sine_samples * data[start:end]) * dt
            avg_q = avg_q + np.sum(cosine_samples * data[start:end]) * dt
        avg_i = avg_i / iq_per_record
        avg_q = avg_q / iq_per_record
        i_values[i] = avg_i
        q_values[i] = avg_q

    return i_values, q_values