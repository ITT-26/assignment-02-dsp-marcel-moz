import sounddevice as sd
import numpy as np
from scipy import signal
from collections import deque


class WhistleInput:

    def __init__(self, input_device, upEventCallback, downEventCallback):
        self.CHUNK_SIZE = 2048  # Number of audio frames per buffer 0.186 seconds
        self.RATE = 44100  # Audio sampling rate (HZ)
        self.CHANNELS = 1  # Mono audio
        self.dominant_freq = None
        self.amplitude = 0
        self.dbfs = 0
        self.isRunning = False
        self.last15Chunks = deque(maxlen=15)
        self.upEventCallback = upEventCallback
        self.downEventCallback = downEventCallback

        # open audio input stream
        self.stream = sd.InputStream(
            device=input_device,
            channels=self.CHANNELS,
            samplerate=self.RATE,
            blocksize=self.CHUNK_SIZE,
            callback=self.audio_callback,
            latency="low",
        )

    def start(self):
        self.stream.start()
        self.isRunning = True

    def stop(self):
        self.isRunning = False
        self.stream.stop()
        self.stream.close()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)

        data = indata[:, 0]  # mono

        data *= np.hamming(
            len(data)
        )  # hamming and convultion based on code from jupyter notebook dsp

        kernel = signal.windows.gaussian(9, 5)  # create a kernel;
        kernel /= np.sum(
            kernel
        )  # normalize the kernel so it does not affect the signal's amplitude

        data = np.convolve(data, kernel, "same")  # apply the kernel to the signal

        fft = np.fft.rfft(data)

        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(data), 1 / self.RATE)

        valid = (freqs >= 80) & (freqs <= 5000)  # higher freq for whistle

        magnitudes = magnitudes[valid]

        freqs = freqs[valid]

        if len(magnitudes) == 0:
            return

        idx = np.argmax(magnitudes)

        dominant_freq = freqs[idx]
        self.dominant_freq = dominant_freq
        self.amplitude = np.sqrt(np.mean(data**2))  ##amplitude calc from ChatGPT
        self.dbfs = 20 * np.log10(self.amplitude + 1e-10)  # db conversion from ChatGPT

        if self.dbfs < -35:
            self.last15Chunks.append(None)
        elif self.dominant_freq is not None and self.dominant_freq < 950:
            # if less then 950 no whistle but speech input or something else
            self.last15Chunks.append(None)
        else:
            self.last15Chunks.append(self.dominant_freq)

        if len(self.last15Chunks) < 15:
            return

        valid_freqs = []

        for freq in self.last15Chunks:
            if freq is not None:
                valid_freqs.append(freq)

        if len(valid_freqs) < 2:
            return

        minFreq = min(valid_freqs)
        maxFreq = max(valid_freqs)

        if maxFreq - minFreq >= 250:
            if valid_freqs.index(minFreq) < valid_freqs.index(maxFreq):
                # min zuerst dann max also von tief nach hoch => pfeil hoch
                self.upEventCallback()
                print("Up Whistle Detected: min: {}, max: {}".format(minFreq, maxFreq))
                self.last15Chunks.clear()  # clear damit nicht nochmal aktion gleich

            elif valid_freqs.index(maxFreq) < valid_freqs.index(minFreq):
                # max zuerst dann max also von hoch nach tief => pfeil runter
                self.downEventCallback()
                print("Down Whistle Detected: min: {}, max: {}".format(minFreq, maxFreq))
                self.last15Chunks.clear()  # clear damit nicht nochmal aktion gleich
