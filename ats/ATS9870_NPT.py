from __future__ import division
import numpy as np
import os
import signal
import sys
import time
import matplotlib.pyplot as plt

# sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'Library'))
import ats.atsapi as ats

class NPT:
    samples_per_sec = 1000000000.0
    # No pre-trigger samples in NPT mode
    pre_trigger_samples = 0
    # TODO: Select the number of samples per record.
    post_trigger_samples = 2048
    # TODO: Select the number of records per DMA buffer.
    records_per_buffer = 100
    # TODO: Select the number of buffers per acquisition.
    buffers_per_acquisition = 100

    def __init__(self, board):
        self.board = board
        self.configure_board()

    def set_range(self, channel, range):
        self.board.inputControl(channel,
                           ats.DC_COUPLING,
                           range,
                           ats.IMPEDANCE_50_OHM)

    # Configures a board for acquisition
    def configure_board(self):
        # TODO: Select clock parameters as required to generate this
        # sample rate
        #
        # For example: if samplesPerSec is 100e6 (100 MS/s), then you can
        # either:
        #  - select clock source INTERNAL_CLOCK and sample rate
        #    SAMPLE_RATE_100MSPS
        #  - or select clock source FAST_EXTERNAL_CLOCK, sample rate
        #    SAMPLE_RATE_USER_DEF, and connect a 100MHz signal to the
        #    EXT CLK BNC connector
        # global samples_per_sec
        self.board.setCaptureClock(ats.EXTERNAL_CLOCK_10MHz_REF,
                              1000000000,
                              ats.CLOCK_EDGE_RISING,
                              1)

        # TODO: Select channel A input parameters as required.
        self.board.inputControl(ats.CHANNEL_A,
                           ats.DC_COUPLING,
                           ats.INPUT_RANGE_PM_400_MV,
                           ats.IMPEDANCE_50_OHM)

        # TODO: Select channel A bandwidth limit as required.
        self.board.setBWLimit(ats.CHANNEL_A, 0)


        # TODO: Select channel B input parameters as required.
        self.board.inputControl(ats.CHANNEL_B,
                           ats.DC_COUPLING,
                           ats.INPUT_RANGE_PM_400_MV,
                           ats.IMPEDANCE_50_OHM)

        # TODO: Select channel B bandwidth limit as required.
        self.board.setBWLimit(ats.CHANNEL_B, 0)

        # TODO: Select trigger inputs and levels as required.
        self.board.setTriggerOperation(ats.TRIG_ENGINE_OP_J,
                                  ats.TRIG_ENGINE_J,
                                  ats.TRIG_EXTERNAL,
                                  ats.TRIGGER_SLOPE_POSITIVE,
                                  132,
                                  ats.TRIG_ENGINE_K,
                                  ats.TRIG_DISABLE,
                                  ats.TRIGGER_SLOPE_POSITIVE,
                                  132)

        # TODO: Select external trigger parameters as required.
        self.board.setExternalTrigger(ats.DC_COUPLING,
                                 ats.ETR_5V)

        # TODO: Set trigger delay as required.
        triggerDelay_sec = 0
        triggerDelay_samples = int(triggerDelay_sec * self.samples_per_sec + 0.5)
        self.board.setTriggerDelay(triggerDelay_samples)

        # TODO: Set trigger timeout as required.
        #
        # NOTE: The board will wait for a for this amount of time for a
        # trigger event.  If a trigger event does not arrive, then the
        # board will automatically trigger. Set the trigger timeout value
        # to 0 to force the board to wait forever for a trigger event.
        #
        # IMPORTANT: The trigger timeout value should be set to zero after
        # appropriate trigger parameters have been determined, otherwise
        # the board may trigger if the timeout interval expires before a
        # hardware trigger event arrives.
        triggerTimeout_sec = 0
        triggerTimeout_clocks = int(triggerTimeout_sec / 10e-6 + 0.5)
        self.board.setTriggerTimeOut(triggerTimeout_clocks)

        # Configure AUX I/O connector as required
        self.board.configureAuxIO(ats.AUX_OUT_TRIGGER,
                             0)


    def acquire_data(self, process_function, verbose = False):
        # TODO: Select the active channels.
        channels = ats.CHANNEL_A | ats.CHANNEL_B
        channelCount = 0
        for c in ats.channels:
            channelCount += (c & channels == c)

        # TODO: Should data be saved to file?
        saveData = False
        dataFile = None
        if saveData:
            dataFile = open(os.path.join(os.path.dirname(__file__),
                                         "data.bin"), 'w')

        # Compute the number of bytes per record and per buffer
        memorySize_samples, bitsPerSample = self.board.getChannelInfo()
        bytesPerSample = (bitsPerSample.value + 7) // 8
        samplesPerRecord = self.pre_trigger_samples + self.post_trigger_samples
        bytesPerRecord = bytesPerSample * samplesPerRecord
        bytesPerBuffer = bytesPerRecord * self.records_per_buffer * channelCount

        # TODO: Select number of DMA buffers to allocate
        bufferCount = 4

        # Allocate DMA buffers
        buffers = []
        for i in range(bufferCount):
            buffers.append(ats.DMABuffer(bytesPerSample, bytesPerBuffer))

        # Set the record size
        self.board.setRecordSize(self.pre_trigger_samples, self.post_trigger_samples)

        recordsPerAcquisition = self.records_per_buffer * self.buffers_per_acquisition

        # Configure the board to make an NPT AutoDMA acquisition
        self.board.beforeAsyncRead(channels,
                                   -self.pre_trigger_samples,
                                   samplesPerRecord,
                                   self.records_per_buffer,
                                   recordsPerAcquisition,
                                   ats.ADMA_EXTERNAL_STARTCAPTURE | ats.ADMA_NPT)



        # Post DMA buffers to board
        for buffer in buffers:
            self.board.postAsyncBuffer(buffer.addr, buffer.size_bytes)

        start = time.clock() # Keep track of when acquisition started
        try:
            self.board.startCapture() # Start the acquisition
            if (verbose):
                print("Capturing %d buffers. Press <enter> to abort" %
                      self.buffers_per_acquisition)
            buffersCompleted = 0
            bytesTransferred = 0
            while (buffersCompleted < self.buffers_per_acquisition and not
                   ats.enter_pressed()):
                # Wait for the buffer at the head of the list of available
                # buffers to be filled by the board.
                buffer = buffers[buffersCompleted % len(buffers)]
                self.board.waitAsyncBufferComplete(buffer.addr, timeout_ms=10000)
                buffersCompleted += 1
                bytesTransferred += buffer.size_bytes

                # TODO: Process sample data in this buffer. Data is available
                # as a NumPy array at buffer.buffer
                process_function(buffer.buffer)
                # NOTE:
                #
                # While you are processing this buffer, the board is already
                # filling the next available buffer(s).
                #
                # You MUST finish processing this buffer and post it back to the
                # board before the board fills all of its available DMA buffers
                # and on-board memory.
                #
                # Samples are arranged in the buffer as follows:
                # S0A, S0B, ..., S1A, S1B, ...
                # with SXY the sample number X of channel Y.
                #
                # Sample code are stored as 8-bit values.
                #
                # Sample codes are unsigned by default. As a result:
                # - 0x00 represents a negative full scale input signal.
                # - 0x80 represents a ~0V signal.
                # - 0xFF represents a positive full scale input signal.
                # Optionaly save data to file
                if dataFile:
                    buffer.buffer.tofile(dataFile)

                # Add the buffer to the end of the list of available buffers.
                self.board.postAsyncBuffer(buffer.addr, buffer.size_bytes)
        finally:
            self.board.abortAsyncRead()
        # Compute the total transfer time, and display performance information.
        transferTime_sec = time.clock() - start
        if (verbose):
            print("Capture completed in %f sec" % transferTime_sec)
        buffersPerSec = 0
        bytesPerSec = 0
        recordsPerSec = 0
        if transferTime_sec > 0:
            buffersPerSec = buffersCompleted / transferTime_sec
            bytesPerSec = bytesTransferred / transferTime_sec
            recordsPerSec = self.records_per_buffer * buffersCompleted / transferTime_sec
        if (verbose):
            print("Captured %d buffers (%f buffers per sec)" %
                (buffersCompleted, buffersPerSec))
        if (verbose):
            print("Captured %d records (%f records per sec)" %
                  (self.records_per_buffer * buffersCompleted, recordsPerSec))
        if (verbose):
            print("Transferred %d bytes (%f bytes per sec)" %
                (bytesTransferred, bytesPerSec))

if __name__ == "__main__":
    board = ats.Board(systemId = 1, boardId = 1)
    npt = NPT(board)
    npt.records_per_buffer = 5
    npt.post_trigger_samples = 1024
    npt.buffers_per_acquisition = 50
    avgd_buffer = np.zeros(npt.post_trigger_samples * npt.records_per_buffer * 2)
    def test_proc(avgd, buffer):
        avgd += buffer
    def avg(buffer):
        test_proc(avgd_buffer, buffer)

    npt.acquire_data(avg, verbose=True)
    plt.plot(avgd_buffer / npt.buffers_per_acquisition)
    plt.show()