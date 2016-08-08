import config
import awg
import visa
from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import dbm.db
import sequence.functions
import matplotlib.pyplot as plt
import acquisition.util

class Onetone_2channel:
    def __init__(self):
        rm = visa.ResourceManager()
        self.awg_inst = rm.open_resource(config.awg_ip)
        self.npt = NPT(atsapi.Board(systemId=1, boardId=1))
        self.rf_cavity = rm.open_resource(config.rfsource_ip)
        self.rf_lo = rm.open_resource(config.rfsource2_ip)
        self.pulse = sequence.sequence.One_Tone(self.awg_inst)

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "1_tone_power", str(id))
        self.pulse.load_from_db(dict["pulse_id"])
        self.npt.post_trigger_samples = int(dict["samples_per_record"])
        self.npt.records_per_buffer = int(dict["records_per_buffer"])
        self.npt.buffers_per_acquisition = int(dict["records_count"])/self.npt.records_per_buffer
        self.if_freq = float(dict["if_freq"])
        self.power_start = float(dict["power_start"])
        self.power_stop = float(dict["power_stop"])
        self.power_steps = float(dict["power_steps"])
        self.frequency_steps = int(dict["freq_steps"])
        self.cav_freq_start = float(dict["cav_freq_start"])
        self.cav_freq_stop = float(dict["cav_freq_stop"])

    def start(self):
        self.pulse.load_waveform()

    def acquire(self):
        awg.set_mode(awg.Runmode.continuous, self.awg_inst)
        ch1, ch2 = acquisition.util.average_buffers(self.awg_inst, self.npt)
        plt.plot(ch1)
        plt.show()
        acquisition.util.iq_demod_subtract(ch1, ch2, self.npt, self.if_freq)



    def close(self):
        self.awg_inst.close()
