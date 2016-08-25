from enum import Enum
import awg
from ats.ATS9870_NPT import NPT
import ats.atsapi as atsapi
import pulse.pulse
import dbm.db
import visa
import numpy as np
import acquisition.util

# class Sequence_Type(Enum):
#     t1 = 1
#     rabi = 2
#     ramsey = 3

class Sequence_2Channel:
    def __init__(self, awg_inst):
        rm = visa.ResourceManager()
        self.awg_inst = awg_inst
        # if type == Sequence_Type.t1:
        #     self.pulse = pulse.pulse.T1_Sequence(self.awg_inst)
        # elif type == Sequence_Type.rabi:
        #     self.pulse = pulse.pulse.Rabi_Sequence(self.awg_inst)
        self.npt = NPT(atsapi.Board(systemId=1, boardId=1))

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "generic_sequence", str(id))
        self.type = dict["pulse_type"];
        if self.type == "t1_pulse":
            self.pulse = pulse.pulse.T1_Sequence(self.awg_inst)
        elif self.type == "rabi_pulse":
            self.pulse = pulse.pulse.Rabi_Sequence(self.awg_inst)
        # if self.type == Sequence_Type.t1:
        #     dict = dbm.db.get_row(cursor, "t1", str(id))
        #     pulse_dict = dbm.db.get_row(cursor, "t1_pulse", dict["pulse_id"])
        # elif self.type == Sequence_Type.rabi:
        #     dict = dbm.db.get_row(cursor, "rabi", str(id))
        #     pulse_dict = dbm.db.get_row(cursor, "rabi_pulse", dict["pulse_id"])
        self.pulse.load_from_db(dict["pulse_id"])
        self.npt.post_trigger_samples = int(dict["samples_per_record"])
        self.npt.buffers_per_acquisition = int(dict["buffers_per_acquisition"])
        # self.npt.records_per_buffer = int(pulse_dict["num_pulses"])
        self.npt.records_per_buffer = self.pulse.num_pulses
        self.if_freq = float(dict["if_frequency"])

    def start(self):
        self.pulse.load_sequence()

    def acquire(self):
        awg.set_mode(awg.Runmode.sequence, self.awg_inst)
        ch1, ch2 = acquisition.util.average_buffers(self.awg_inst, self.npt)
        mag, phase = acquisition.util.iq_demod_subtract(ch1, ch2, self.npt, self.if_freq)
        time = np.linspace(0, self.pulse.t_inc * self.pulse.num_pulses, self.pulse.num_pulses, endpoint=False)
        return time, mag, phase