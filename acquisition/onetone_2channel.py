import config
import awg
import visa
from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import dbm.db
import pulse.functions
import pulse.pulse
import matplotlib.pyplot as plt
import acquisition.util
import numpy as np

class Onetone_Power:
    def __init__(self):
        self.onetone = Onetone_2channel()

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "1_tone_power", str(id))
        self.onetone.pulse.load_from_db(dict["pulse_id"])
        self.onetone.npt.post_trigger_samples = int(dict["samples_per_record"])
        self.onetone.npt.records_per_buffer = int(dict["records_per_buffer"])
        self.onetone.npt.buffers_per_acquisition = int(dict["records_count"])/self.onetone.npt.records_per_buffer
        self.onetone.if_freq = float(dict["if_freq"])

    def start(self):
        self.onetone.start()

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
            if (verbose):
                print("f=" + str(self.rf_source.get_freq()))
            mag, phase = self.one_tone.acquire()
            mags[i] = mag
            phases[i] = phase

        self.rf_source.enable(False)
        self.lo_source.enable(False)
        return freqs, mags, np.unwrap(phases)

class Onetone_2channel:
    def __init__(self, awg_inst):
        rm = visa.ResourceManager()
        self.awg_inst = awg_inst
        self.npt = NPT(atsapi.Board(systemId=1, boardId=1))
        self.rf_cavity = rm.open_resource(config.rfsource_ip)
        self.rf_lo = rm.open_resource(config.rfsource2_ip)
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
        return np.mean(mag), np.mean(phase)
