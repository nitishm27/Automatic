import sequence.functions
import awg
import dbm.db

def set_goto_sequence(index, inst):
    index = index - 1
    for i in range(index):
        if i == (index - 1):
            awg.set_goto(i + 1, 1, inst)
        else:
            awg.set_goto(i + 1, i + 2, inst)

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
            return int(float(dict[value])/self.clock)
        self.samples = int(dict["samples"])
        self.num_pulses = int(dict["num_pulses"])
        self.qubit_end_time = parse("qubit_end_time")
        self.qubit_width = parse("qubit_width")
        self.cavity_width = parse("cavity_width")
        self.marker_width = parse("marker_width")
        self.delay_const1 = parse("delay_const1")
        self.delay_const2 = parse("delay_const2")
        self.t_inc = parse("t_inc")

    def load_sequence(self):
        gaussian, gaussian_empty = sequence.functions.gen_gaussian(self.qubit_width)
        cavity, marker, cavity_empty = sequence.functions.gen_cavity(self.cavity_width, self.delay_const2, self.marker_width)
        t_inc_wait = sequence.functions.gen_space(self.t_inc)
        start_wait = sequence.functions.gen_space(self.qubit_end_time - 4 * self.qubit_width - self.delay_const1 - self.num_pulses * self.t_inc)
        end_wait = sequence.functions.gen_space(self.samples - self.cavity_width - self.qubit_end_time)
        delay1_wait = sequence.functions.gen_space(self.delay_const1)
        awg.add_waveform(gaussian, "qubit", self.inst)
        awg.add_waveform(gaussian_empty, "qubit_empty", self.inst)
        awg.add_waveform(cavity, "cavity", self.inst, marker1=marker)
        awg.add_waveform(cavity_empty, "cavity_empty", self.inst)
        awg.add_waveform(t_inc_wait, "t_inc_wait", self.inst)
        awg.add_waveform(start_wait, "start_wait", self.inst)
        awg.add_waveform(end_wait, "end_wait", self.inst)
        awg.add_waveform(delay1_wait, "delay1_wait", self.inst)
        awg.clear_sequence(self.inst)

        index = 1
        for i in range(self.num_pulses):
            awg.add_to_sequence(1, "start_wait", index, self.inst)
            awg.add_to_sequence(2, "start_wait", index, self.inst)
            index = index + 1
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
            awg.add_to_sequence(1, "delay1_wait", index, self.inst)
            awg.add_to_sequence(2, "delay1_wait", index, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "cavity_empty", index, self.inst)
            awg.add_to_sequence(2, "cavity", index, self.inst)
            index = index + 1
            awg.add_to_sequence(1, "end_wait", index, self.inst)
            awg.add_to_sequence(2, "end_wait", index, self.inst)
            index = index + 1

        set_goto_sequence(index, self.inst)


