import sounddevice as sd
import numpy as np
from scipy import signal


class SoundInput:

    def __init__(self, input_device):
        self.CHUNK_SIZE = 512  # Number of audio frames per buffer
        self.RATE = 44100  # Audio sampling rate (HZ)
        self.CHANNELS = 1  # Mono audio
        self.dominant_freq = None
        self.amplitude = 0
        self.dbfs = 0
        self.isRunning = False
        
       

        # open audio input stream
        self.stream = sd.InputStream(
            device=input_device,
            channels=self.CHANNELS,
            samplerate=self.RATE,
            blocksize=self.CHUNK_SIZE,
            callback=self.audio_callback,
            latency="low"
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
        data *= np.hamming(len(data)) # code from jupyter notebook dsp
        
        KERNEL_SIZE = 5
        KERNEL_SIGMA = 10
        kernel = signal.windows.gaussian(KERNEL_SIZE, KERNEL_SIGMA) # create a kernel
        kernel /= np.sum(kernel)
        
        data2 =  np.convolve(data, kernel, 'same')
        
        fft = np.fft.fft(data2)
        frequencyStrength = np.abs(fft)

        freqs = np.fft.fftfreq(len(data2), 1 / self.RATE)

        # only positive frequencies
        positive = freqs > 0
        freqs = freqs[positive]
        frequencyStrength = frequencyStrength[positive]

        # dominant frequency
        dominant_freq = freqs[np.argmax(frequencyStrength)]
        self.dominant_freq = dominant_freq
        self.amplitude = np.sqrt(np.mean(data ** 2)) ##amplitude calc from ChatGPT
        self.dbfs = 20 * np.log10(self.amplitude + 1e-10)  # db conversion from ChatGPT

    def freq_to_karaoke_midi(self, prev_midi=None): # method from ChatGpt
        freq = self.dominant_freq
        if freq is None:
            return
        if freq <= 0:
            return None

        midi = 69 + 12 * np.log2(freq / 440.0)
        midi = int(round(midi))

        # octave correction range for voice
        while midi < 45:
            midi += 12
        while midi > 75:
            midi -= 12

        # smoothing (prevents jumping)
        if prev_midi is not None and abs(midi - prev_midi) > 5:
            return prev_midi

        return midi
