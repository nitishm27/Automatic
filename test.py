import acquisition.sequence_2channel as sq
import acquisition.onetone_2channel as con
# t1_sequence = sq.Sequence_2Channel(sq.Sequence_Type.t1)
# t1_sequence.load_from_db(3)
# t1_sequence.npt.buffers_per_acquisition = 1000
# t1_sequence.start()
# t1_sequence.acquire()
# t1_sequence.close()

one_tone = con.Onetone_2channel()
one_tone.load_from_db(5)
one_tone.npt.buffers_per_acquisition = 1000
one_tone.start()
one_tone.acquire()
one_tone.close()















