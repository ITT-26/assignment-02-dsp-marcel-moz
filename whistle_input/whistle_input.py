import pyglet
import sounddevice as sd
from WhistleInput import WhistleInput
from pyglet import window


print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev["max_input_channels"] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

        # let user select audio device
input_device = int(input("\nSelect input device: "))



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


input = WhistleInput(input_device, upEventCallback=moveRectangleSelectionUp, downEventCallback=moveRectangleSelectionDown)
input.start()


try:
    pyglet.app.run()
except KeyboardInterrupt:
    print("programm stop")
    input.stop()
    pyglet.app.exit()
