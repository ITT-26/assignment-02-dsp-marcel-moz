import sounddevice as sd
import numpy as np
from scipy import signal


class SoundInput:

    def __init__(self, input_device):
        self.CHUNK_SIZE = 8192  # Number of audio frames per buffer 0.186 seconds 
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
        
        data *= np.hamming(len(data)) # hamming and convultion based on code from jupyter notebook dsp
        
        kernel = signal.windows.gaussian(9, 5) # create a kernel; 
        kernel /= np.sum(kernel) # normalize the kernel so it does not affect the signal's amplitude
           
        data = np.convolve(data, kernel, 'same') # apply the kernel to the signal
    
        
        fft = np.fft.rfft(data)
        
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(data), 1 / self.RATE)

        valid = (freqs >= 80) & (freqs <= 1000) # human voice freq from chat gpt
        
        magnitudes = magnitudes[valid]

        freqs = freqs[valid]
    

        if len(magnitudes) == 0:
            return


        
        idx = np.argmax(magnitudes)
        
        dominant_freq = freqs[idx]
        self.dominant_freq = dominant_freq
        self.amplitude = np.sqrt(np.mean(data ** 2)) ##amplitude calc from ChatGPT
        self.dbfs = 20 * np.log10(self.amplitude + 1e-10)  # db conversion from ChatGPT

    def freq_to_karaoke_midi(self): # method from ChatGpt
        freq = self.dominant_freq
        if freq is None:
            return
        if freq <= 0:
            return None

        midi = 69 + 12 * np.log2(freq / 440.0)
        midi = int(round(midi))


        return midi
