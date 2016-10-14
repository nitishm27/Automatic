import dbm.db
import numpy as np

import pulse.functions
from instruments import awg


def set_goto_sequence(index, inst):
    index = index - 1
    for i in range(index):
        if i == (index - 1):
            awg.set_goto(i + 1, 1, inst)
        else:
            awg.set_goto(i + 1, i + 2, inst)

class Continuous:
    id = -1

    def __init__(self, inst):
        self.inst = inst

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "continuous_pulse", str(id))

        self.clock = float(dict["clock"])

        def parse(value):
            return int(np.round(float(dict[value]) / self.clock))

        self.samples = int(dict["samples"])
        self.qubit_peak = parse("qubit_pulse_peak")
        self.qubit_width = parse("qubit_pulse_width")
        self.cavity_width = parse("cavity_pulse_width")
        self.cavity_start = parse("cavity_pulse_start")
        self.marker_width = parse("marker_width")
        self.delay_const1 = parse("delay_const_1")
        self.delay_const2 = parse("delay_const_2")
        self.qubit_on = bool(dict["qubit_on"])

    def load_waveform(self):
        if(self.qubit_on):
            gaussian, gaussian_empty = pulse.functions.gen_gaussian(self.qubit_width)
            channel1 = np.zeros(self.samples)
            channel1[(self.qubit_peak - 2 * self.qubit_width): (self.qubit_peak + 2 * self.qubit_width)] = gaussian
            awg.add_waveform(channel1, "1_tone_qubit", self.inst)
            awg.add_to_continuous(1, "1_tone_qubit", self.inst)
        cavity, marker, cavity_empty = pulse.functions.gen_cavity(self.cavity_width, self.delay_const2, self.marker_width)
        channel2 = np.zeros(self.samples)
        channel2[(self.cavity_start): (self.cavity_start + self.cavity_width)] = cavity
        channel2_marker = np.zeros(len(channel1))
        channel2_marker[(self.cavity_start): (self.cavity_start + self.cavity_width)] = marker
        awg.add_waveform(channel2, "1_tone_cavity", self.inst, marker1=channel2_marker)
        awg.add_to_continuous(2, "1_tone_cavity", self.inst)

class Rabi_Sequence:
    id = -1

    def __init__(self, inst):
        self.inst = inst

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "rabi_pulse", str(id))

        self.clock = float(dict["clock"])

        def parse(value):
            return int(np.round(float(dict[value]) / self.clock))

        self.samples = int(dict["samples"])
        self.num_pulses = int(dict["num_pulses"])
        self.qubit_end_time = parse("qubit_end_time")
        self.qubit_start_width = parse("qubit_start_width")
        self.cavity_width = parse("cavity_width")
        self.marker_width = parse("marker_width")
        self.delay_const1 = parse("delay_const1")
        self.delay_const2 = parse("delay_const2")
        self.t_inc = parse("t_inc")

    def load_sequence(self):
        cavity, marker, cavity_empty = pulse.functions.gen_cavity(self.cavity_width, self.delay_const2, self.marker_width)
        qubit_wait = pulse.functions.gen_space(4 * (self.qubit_start_width + (self.num_pulses - 1) * self.t_inc) + self.delay_const1)
        qubit = pulse.functions.gen_space(len(qubit_wait))
        start_wait = pulse.functions.gen_space(self.qubit_end_time - len(qubit_wait) + self.delay_const1)
        end_wait = pulse.functions.gen_space(self.samples - self.qubit_end_time - self.delay_const1 - self.cavity_width)
        awg.add_waveform(cavity, "cavity", self.inst, marker1=marker)
        awg.add_waveform(cavity_empty, "cavity_empty", self.inst)
        awg.add_waveform(start_wait, "start_wait", self.inst)
        awg.add_waveform(end_wait, "end_wait", self.inst)
        awg.add_waveform(qubit_wait, "qubit_wait", self.inst)
        awg.clear_sequence(self.inst)

        index = 1
        for i in range(self.num_pulses):
            awg.add_to_sequence(1, "start_wait", index, self.inst)
            awg.add_to_sequence(2, "start_wait", index, self.inst)
            index = index + 1
            self.add_qubit(qubit, self.qubit_start_width + self.t_inc * i, index)
            index = index + 1
            awg.add_to_sequence(1, "cavity_empty", index, self.inst)
            awg.add_to_sequence(2, "cavity", index, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "end_wait", index, self.inst)
            awg.add_to_sequence(2, "end_wait", index, self.inst)
            index = index + 1

        set_goto_sequence(index, self.inst)

    def add_qubit(self, arr, width, index):
        gaussian = pulse.functions.gen_gaussian(width)[0]
        arr[-1 * (self.delay_const1 + 4 * width):-1 * self.delay_const1] = gaussian
        awg.add_waveform(arr, "qubit_" + str(width), self.inst)
        awg.add_to_sequence(1, "qubit_" + str(width), index, self.inst)
        awg.add_to_sequence(2, "qubit_wait", index, self.inst)

class T1_Sequence:
    id = -1

    def __init__(self, inst):
        self.inst = inst

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "t1_pulse", str(id))

        self.clock = float(dict["clock"])
        def parse(value):
            return int(np.round(float(dict[value])/self.clock))
        self.samples = int(dict["samples"])
        self.num_pulses = int(dict["num_pulses"])
        # self.qubit_end_time = parse("qubit_end_time")
        self.qubit_width = parse("qubit_width")
        self.cavity_width = parse("cavity_width")
        self.marker_width = parse("marker_width")
        # self.delay_const1 = parse("delay_const1")
        self.delay_const2 = parse("delay_const2")
        self.pulse_type = dict["qubit_pulse_type"]
        if self.pulse_type == "gaussian_edge":
            self.edge_width = parse("qubit_edge_width")
        self.t_inc = parse("t_inc")

    def load_sequence(self):
        if self.pulse_type == "gaussian":
            qubit, qubit_empty = pulse.functions.gen_gaussian(self.qubit_width)
        elif self.pulse_type == "gaussian_edge":
            qubit, qubit_empty = pulse.functions.gen_gaussian_edge(self.edge_width, self.qubit_width)

        cavity, marker, cavity_empty = pulse.functions.gen_cavity(self.cavity_width, self.delay_const2, self.marker_width)
        t_inc_wait = pulse.functions.gen_space(self.t_inc)
        # start_wait = pulse.functions.gen_space(self.qubit_end_time - 4 * self.qubit_width - self.delay_const1 - self.num_pulses * self.t_inc)
        end_wait = pulse.functions.gen_space(self.samples - self.cavity_width - len(qubit) - self.num_pulses * self.t_inc)
        # delay1_wait = pulse.functions.gen_space(self.delay_const1)
        awg.add_waveform(qubit, "qubit", self.inst)
        awg.add_waveform(qubit_empty, "qubit_empty", self.inst)
        awg.add_waveform(cavity, "cavity", self.inst, marker1=marker)
        awg.add_waveform(cavity_empty, "cavity_empty", self.inst)
        awg.add_waveform(t_inc_wait, "t_inc_wait", self.inst)
        # awg.add_waveform(start_wait, "start_wait", self.inst)
        awg.add_waveform(end_wait, "end_wait", self.inst)
        # awg.add_waveform(delay1_wait, "delay1_wait", self.inst)
        awg.clear_sequence(self.inst)

        index = 1
        for i in range(self.num_pulses):
            # awg.add_to_sequence(1, "start_wait", index, self.inst)
            # awg.add_to_sequence(2, "start_wait", index, self.inst)
            # index = index + 1
            awg.add_to_sequence(1, "t_inc_wait", index, self.inst)
            awg.add_to_sequence(2, "t_inc_wait", index, self.inst)
            awg.set_repeat(index, self.num_pulses - i, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "qubit", index, self.inst)
            awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            index = index + 1
            if i > 0:
                awg.add_to_sequence(1, "t_inc_wait", index, self.inst)
                awg.add_to_sequence(2, "t_inc_wait", index, self.inst)
                awg.set_repeat(index, i, self.inst)
                index = index + 1
            # awg.add_to_sequence(1, "delay1_wait", index, self.inst)
            # awg.add_to_sequence(2, "delay1_wait", index, self.inst)
            # index = index + 1
            awg.add_to_sequence(1, "cavity_empty", index, self.inst)
            awg.add_to_sequence(2, "cavity", index, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "end_wait", index, self.inst)
            awg.add_to_sequence(2, "end_wait", index, self.inst)
            index = index + 1

        set_goto_sequence(index, self.inst)

class T2_Sequence:
    id = -1

    def __init__(self, inst):
        self.inst = inst

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "t2_pulse", str(id))

        self.clock = float(dict["clock"])
        def parse(value):
            return int(np.round(float(dict[value])/self.clock))
        self.samples = int(dict["samples"])
        self.num_pulses = int(dict["num_pulses"])
        self.qubit_width = parse("qubit_width")
        self.cavity_width = parse("cavity_width")
        self.marker_width = parse("marker_width")
        self.delay_const2 = parse("delay_const2")
        self.pulse_type = dict["qubit_pulse_type"]
        if self.pulse_type == "gaussian_edge":
            self.qubit_edge_with = parse("qubit_edge_width")
        self.t_inc = parse("t_inc")

    def load_sequence(self):

        qubit = pulse.functions.gen_gaussian(self.qubit_width)[0]
        cavity, marker, cavity_empty = pulse.functions.gen_cavity(self.cavity_width, self.delay_const2, self.marker_width)
        t_inc_wait = pulse.functions.gen_space(self.t_inc)
        end_wait = pulse.functions.gen_space(self.samples - self.cavity_width - \
                                             2 * len(qubit) - self.num_pulses * self.t_inc)
        qubit_double_len = 2 * len(qubit) + self.num_pulses * self.t_inc
        qubit_double_empty = np.zeros(qubit_double_len)
        awg.add_waveform(qubit_double_empty, "qubit_empty", self.inst)
        # awg.add_waveform(qubit, "qubit", self.inst)
        # awg.add_waveform(qubit_empty, "qubit_empty", self.inst)
        awg.add_waveform(cavity, "cavity", self.inst, marker1=marker)
        awg.add_waveform(cavity_empty, "cavity_empty", self.inst)
        awg.add_waveform(t_inc_wait, "t_inc_wait", self.inst)
        awg.add_waveform(end_wait, "end_wait", self.inst)
        awg.clear_sequence(self.inst)

        index = 1
        for i in range(self.num_pulses):
            qubit_double_pulse = np.zeros(qubit_double_len)
            qubit_double_pulse[-1 * len(qubit):len(qubit_double_pulse)] = qubit
            qubit_double_pulse[-1 *(2*len(qubit) + i * self.t_inc):-1 *(len(qubit) + i * self.t_inc)] = qubit
            name = "qubit_" + str(i)
            awg.add_waveform(qubit_double_pulse, name, self.inst)
            awg.add_to_sequence(1, name, index, self.inst)
            awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            index = index + 1
            # awg.add_to_sequence(1, "t_inc_wait", index, self.inst)
            # awg.add_to_sequence(2, "t_inc_wait", index, self.inst)
            # awg.set_repeat(index, self.num_pulses - i, self.inst)
            # index = index + 1
            # awg.add_to_sequence(1, "qubit", index, self.inst)
            # awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            # index = index + 1
            # awg.add_to_sequence(1, "t_inc_wait", index, self.inst)
            # awg.add_to_sequence(2, "t_inc_wait", index, self.inst)
            # awg.set_repeat(index, i + 1, self.inst)
            # index = index + 1
            # awg.add_to_sequence(1, "qubit", index, self.inst)
            # awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            # index = index + 1
            awg.add_to_sequence(1, "cavity_empty", index, self.inst)
            awg.add_to_sequence(2, "cavity", index, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "end_wait", index, self.inst)
            awg.add_to_sequence(2, "end_wait", index, self.inst)
            index = index + 1

        set_goto_sequence(index, self.inst)

class T2_echo_Sequence:
    id = -1

    def __init__(self, inst):
        self.inst = inst

    def load_from_db(self, id):
        self.id = id
        cnx = dbm.db.open_readonly_connection()
        cursor = cnx.cursor()
        dict = dbm.db.get_row(cursor, "t2_pulse", str(id))

        self.clock = float(dict["clock"])
        def parse(value):
            return int(np.round(float(dict[value])/self.clock))
        self.samples = int(dict["samples"])
        self.num_pulses = int(dict["num_pulses"])
        self.qubit_width = parse("qubit_width")
        self.qubit_width_pi = parse("qubit_width_pi")
        self.cavity_width = parse("cavity_width")
        self.marker_width = parse("marker_width")
        self.delay_const2 = parse("delay_const2")
        self.pulse_type = dict["qubit_pulse_type"]
        if self.pulse_type == "gaussian_edge":
            self.qubit_edge_with = parse("qubit_edge_width")
        self.t_inc = parse("t_inc")

    def load_sequence(self):

        qubit = pulse.functions.gen_gaussian(self.qubit_width)[0]
        qubit_pi = pulse.functions.gen_gaussian(self.qubit_width_pi)[0]
        cavity, marker, cavity_empty = pulse.functions.gen_cavity(self.cavity_width, self.delay_const2, self.marker_width)
        t_inc_wait = pulse.functions.gen_space(self.t_inc)
        end_wait = pulse.functions.gen_space(self.samples - self.cavity_width - \
                                             2 * len(qubit) - self.num_pulses * self.t_inc)
        qubit_double_len = 2 * len(qubit) + len(qubit_pi) + self.num_pulses * self.t_inc * 2
        qubit_double_empty = np.zeros(qubit_double_len)
        awg.add_waveform(qubit_double_empty, "qubit_empty", self.inst)
        # awg.add_waveform(qubit, "qubit", self.inst)
        # awg.add_waveform(qubit_empty, "qubit_empty", self.inst)
        awg.add_waveform(cavity, "cavity", self.inst, marker1=marker)
        awg.add_waveform(cavity_empty, "cavity_empty", self.inst)
        awg.add_waveform(t_inc_wait, "t_inc_wait", self.inst)
        awg.add_waveform(end_wait, "end_wait", self.inst)
        awg.clear_sequence(self.inst)

        index = 1
        for i in range(self.num_pulses):
            qubit_double_pulse = np.zeros(qubit_double_len)
            qubit_double_pulse[-1 * len(qubit)::] = qubit
            qubit_double_pulse[-1 *(len(qubit) + len(qubit_pi) + i * self.t_inc) : -1 *(len(qubit) + i * self.t_inc)] = qubit_pi
            qubit_double_pulse[-1 * (2*len(qubit) + len(qubit_pi) + 2*i * self.t_inc) : -1 * (len(qubit) + len(qubit_pi) + 2*i * self.t_inc)] = qubit

            name = "qubit_" + str(i)
            awg.add_waveform(qubit_double_pulse, name, self.inst)
            awg.add_to_sequence(1, name, index, self.inst)
            awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            index = index + 1
            # awg.add_to_sequence(1, "t_inc_wait", index, self.inst)
            # awg.add_to_sequence(2, "t_inc_wait", index, self.inst)
            # awg.set_repeat(index, self.num_pulses - i, self.inst)
            # index = index + 1
            # awg.add_to_sequence(1, "qubit", index, self.inst)
            # awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            # index = index + 1
            # awg.add_to_sequence(1, "t_inc_wait", index, self.inst)
            # awg.add_to_sequence(2, "t_inc_wait", index, self.inst)
            # awg.set_repeat(index, i + 1, self.inst)
            # index = index + 1
            # awg.add_to_sequence(1, "qubit", index, self.inst)
            # awg.add_to_sequence(2, "qubit_empty", index, self.inst)
            # index = index + 1
            awg.add_to_sequence(1, "cavity_empty", index, self.inst)
            awg.add_to_sequence(2, "cavity", index, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "end_wait", index, self.inst)
            awg.add_to_sequence(2, "end_wait", index, self.inst)
            index = index + 1

        set_goto_sequence(index, self.inst)

