import sounddevice as sd
from WhistleInput import WhistleInput
from pynput.keyboard import Controller, Key
import time


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



keyboard = Controller()


def handleEventUp():
    keyboard.press(Key.up)
    keyboard.release(Key.up)


def handleEventDown():
    keyboard.press(Key.down)
    keyboard.release(Key.down)

input = WhistleInput(input_device, upEventCallback=handleEventUp, downEventCallback=handleEventDown)

try:
    input.start()
    while input.isRunning:
         time.sleep(1)
except KeyboardInterrupt:
    print("programm stop")
    input.stop()

