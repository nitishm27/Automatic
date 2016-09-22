import dbm.db
import numpy as np

import acquisition.util
import ats.atsapi as atsapi
import pulse.functions
import pulse.pulse
from ats.ATS9870_NPT import NPT
from instruments import awg


class Onetone_Power:
    def __init__(self, awg_inst, lo_source, rf_source):
        self.one_tone = Continuous()
        self.awg_inst = awg_inst
        self.lo_source = lo_source
        self.rf_source = rf_source
        self.onetone_freq = Onetone_Frequency(self.awg_inst, self.lo_source, self.rf_source, self.one_tone)

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "1_tone_power", str(id))
        self.one_tone.pulse.load_from_db(dict["pulse_id"])
        self.one_tone.npt.post_trigger_samples = int(dict["samples_per_record"])
        self.one_tone.npt.records_per_buffer = int(dict["records_per_buffer"])
        self.one_tone.npt.buffers_per_acquisition = int(dict["records_count"]) / self.one_tone.npt.records_per_buffer
        self.one_tone.if_freq = float(dict["if_freq"])
        self.power_start = float(dict["power_start"])
        self.power_stop = float(dict["power_stop"])
        self.power_steps = float(dict["power_steps"])
        self.freq_start = float(dict["cav_freq_start"])
        self.freq_stop = float(dict["cav_freq_stop"])
        self.freq_steps = float(dict["freq_steps"])

    def start(self):
        self.one_tone_freq.start()

    def acquire(self, verbose=False):
        powers = np.zeros(self.power_steps*self.freq_steps)
        frequencies = np.zeros(len(powers))
        magnitudes = np.zeros(len(powers))
        phases = np.zeros(len(powers))

        powers_list = np.linspace(self.power_start, self.power_stop, self.power_steps)
        for i, power in enumerate(powers_list):
            self.rf_source.set_power(power)
            if verbose:
                print("p=" + str(self.rf_source.get_power()))
            freq_slice, mag_slice, phase_slice = \
                self.one_tone_freq.acquire(self.freq_start, self.freq_stop, self.freq_steps, verbose=verbose)
            powers[i*self.freq_steps:(i+1)*self.freq_steps] = power
            frequencies[i * self.freq_steps:(i + 1) * self.freq_steps] = freq_slice
            magnitudes[i*self.freq_steps:(i+1)*self.freq_steps] = mag_slice
            phases[i*self.freq_steps:(i+1)*self.freq_steps] = phase_slice

        return powers, frequencies, magnitudes, phases

class Twotone_Frequency:
    def __init__(self, awg_inst, qubit_source, two_tone):
        self.awg_inst = awg_inst
        self.two_tone = two_tone
        self.qubit_source = qubit_source

    def start(self):
        self.two_tone.start()

    def acquire(self, start_freq, end_freq, freq_steps, verbose=False):
        self.qubit_source.set_iq(True)
        self.qubit_source.set_ext_clock(True)
        self.qubit_source.enable(True)

        freqs = np.linspace(start_freq, end_freq, freq_steps)
        mags = np.zeros(len(freqs))
        phases = np.zeros(len(freqs))
        for i,freq in enumerate(freqs):
            self.qubit_source.set_freq(freq/1e9)
            if verbose:
                print("f=" + str(self.qubit_source.get_freq()))
            mag, phase = self.two_tone.acquire()
            mags[i] = np.mean(mag)
            phases[i] = np.mean(phase)

        self.qubit_source.enable(False)
        return freqs, mags, np.unwrap(phases)

class Onetone_Frequency:
    def __init__(self, awg_inst, lo_source, rf_source, one_tone):
        self.awg_inst = awg_inst
        self.lo_source = lo_source
        self.rf_source = rf_source
        self.one_tone = one_tone

    def start(self):
        self.one_tone.start()

    def acquire(self, start_freq, end_freq, freq_steps, verbose=False):
        self.rf_source.set_iq(True)
        self.lo_source.set_iq(False)
        self.rf_source.set_ext_clock(True)
        self.lo_source.set_ext_clock(True)
        self.rf_source.enable(True)
        self.lo_source.enable(True)

        freqs = np.linspace(start_freq, end_freq, freq_steps)
        mags = np.zeros(len(freqs))
        phases = np.zeros(len(freqs))
        for i,freq in enumerate(freqs):
            self.rf_source.set_freq(freq/1e9)
            self.lo_source.set_freq((self.one_tone.if_freq + freq)/1e9)
            if verbose:
                print("f=" + str(self.rf_source.get_freq()))
            mag, phase = self.one_tone.acquire()
            mags[i] = np.mean(mag)
            phases[i] = np.mean(phase)

        self.rf_source.enable(False)
        self.lo_source.enable(False)
        return freqs, mags, np.unwrap(phases)

class Continuous:
    def __init__(self, awg_inst):
        self.awg_inst = awg_inst
        self.npt = NPT(atsapi.Board(systemId=1, boardId=1))
        self.pulse = pulse.pulse.Continuous(self.awg_inst)

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "1_tone", str(id))
        self.pulse.load_from_db(dict["pulse_id"])
        self.npt.post_trigger_samples = int(dict["samples_per_record"])
        self.npt.records_per_buffer = int(dict["records_per_buffer"])
        self.npt.buffers_per_acquisition = int(float(dict["records_count"])/self.npt.records_per_buffer)
        self.if_freq = float(dict["if_freq"])

    def start(self):
        self.pulse.load_waveform()

    def acquire(self):
        awg.set_mode(awg.Runmode.continuous, self.awg_inst)
        ch1, ch2 = acquisition.util.average_buffers(self.awg_inst, self.npt)
        mag, phase = acquisition.util.iq_demod_subtract(ch1, ch2, self.npt, self.if_freq)
        return mag, phase
