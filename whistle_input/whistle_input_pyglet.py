import pyglet
import sounddevice as sd
from SoundInput import SoundInput
from pyglet import window
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

win = window.Window()


dis = pyglet.display.get_display()
screen = dis.get_default_screen()
win.height = screen.height // 4 * 3
win.width = screen.width // 3


rectangles = {}

batch = pyglet.graphics.Batch()

GREY = (150, 150, 150)
GREEN = (0, 255, 0)

for i in range(9):
    rect = pyglet.shapes.Rectangle(
        x=50,
        y=((win.height // 9) * i) + 25,
        width=win.width - 100,
        height=(win.height // 9) - 50,
        color=GREY,
        batch=batch,
    )
    rectangles[i] = rect


rectangles[4].color = GREEN  # highlight center rect in beginning
markedRectIdx = 4


@win.event
def on_draw():
    win.clear()
    batch.draw()


def moveRectangleSelectionUp():
    global markedRectIdx

    if markedRectIdx == len(rectangles) - 1:
        return  # return wenn schon ganz oben
    else:
        rectangles[markedRectIdx].color = GREY
        rectangles[markedRectIdx + 1].color = GREEN
        markedRectIdx += 1


def moveRectangleSelectionDown():
    global markedRectIdx

    if markedRectIdx == 0:
        return  # return wenn schon ganz unten
    else:
        rectangles[markedRectIdx].color = GREY
        rectangles[markedRectIdx - 1].color = GREEN
        markedRectIdx -= 1


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
            moveRectangleSelectionUp()
            # print("min: {}, max: {}".format(minFreq, maxFreq))
            last2SecFreqs.clear()  # clear damit nicht nochmal aktion gleich
        elif valid_freqs.index(maxFreq) < valid_freqs.index(minFreq):
            # max zuerst dann max also von hoch nach tief => pfeil runter
            moveRectangleSelectionDown()
            # print("min: {}, max: {}".format(minFreq, maxFreq))
            last2SecFreqs.clear()  # clear damit nicht nochmal aktion gleich


pyglet.clock.schedule_interval(update, 0.2)  # 5 per sec


try:
    pyglet.app.run()
except KeyboardInterrupt:
    print("programm stop")
    soundInput.stop()
    pyglet.app.exit()
