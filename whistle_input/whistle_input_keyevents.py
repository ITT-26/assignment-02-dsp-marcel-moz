import sounddevice as sd
from SoundInput import SoundInput
from pynput.keyboard import Controller, Key
import pyglet

from collections import deque

print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev["max_input_channels"] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

        # let user select audio device
input_device = int(input("\nSelect input device: "))

soundInput = SoundInput(input_device)

keyboard = Controller()


def handleEventUp():
    keyboard.press(Key.up)
    keyboard.release(Key.up)


def handleEventDown():
    keyboard.press(Key.down)
    keyboard.release(Key.down)


soundInput.start()

last2SecFreqs = deque(maxlen=10)


def update(dt):

    if soundInput.dbfs < -35:
        last2SecFreqs.append(None)

    elif (
        soundInput.dominant_freq is not None and soundInput.dominant_freq < 950
    ):  # if less then 950 no whistle but speech input or something else
        last2SecFreqs.append(None)
    else:
        last2SecFreqs.append(soundInput.dominant_freq)

    if len(last2SecFreqs) < 5:
        return

    valid_freqs = []

    for freq in last2SecFreqs:
        if freq is not None:
            valid_freqs.append(freq)

    if len(valid_freqs) < 2:
        return

    minFreq = min(valid_freqs)
    maxFreq = max(valid_freqs)

    if maxFreq - minFreq >= 150:
        if valid_freqs.index(minFreq) < valid_freqs.index(maxFreq):
            # min zuerst dann max also von tief nach hoch => pfeil hoch
            handleEventUp()
            print("Up Whistle Detected: min: {}, max: {}".format(minFreq, maxFreq))
            last2SecFreqs.clear()  # clear damit nicht nochmal aktion gleich
        elif valid_freqs.index(maxFreq) < valid_freqs.index(minFreq):
            # max zuerst dann max also von hoch nach tief => pfeil runter
            handleEventDown()
            print("Down Whitle Detected: min: {}, max: {}".format(minFreq, maxFreq))
            last2SecFreqs.clear()  # clear damit nicht nochmal aktion gleich


pyglet.clock.schedule_interval(update, 0.2)

try:
    pyglet.app.run()
except KeyboardInterrupt:
    print("programm stop")
    soundInput.stop()
    pyglet.app.exit()
