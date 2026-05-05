import pyglet, WindowHandling, sys
import sounddevice as sd
from ObjectCreator import ObjectCreator
from MidiPlayer import MidiPlayer
from SoundInput import SoundInput
from pyglet import window
from pyglet.window import key

if len(sys.argv) < 2:
    print("Please specify a path: python main.py /path/to/midi_file.mid")
    sys.exit(1)
else:
    path = sys.argv[1]

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
WindowHandling.setup_window(win)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.Group(order=0)
noteGroup = pyglet.graphics.Group(order=1)
foreground = pyglet.graphics.Group(order=2)


objectCreator = ObjectCreator(win, batch)
player = MidiPlayer()

lines = objectCreator.createLines(background)


sung_note_rects = []


@win.event
def on_close():
    pyglet.app.exit()


@win.event
def on_draw():
    win.clear()
    batch.draw()


def setupTrack(path):
    player.readFile(path)
    notes = objectCreator.createNoteRectangles(player.messages, noteGroup)
    return notes


def buildTimedMessages(
    messages,
):  # method basend on ChatGPT suggestions for fixing timing
    timedMsg = []
    current_time = 0

    for msg in messages:
        current_time += msg.time
        timedMsg.append((current_time, msg))

    return timedMsg





gameStarted = False
gameEnded = False
notes = []
timedMessages = []
msg_index = 0
audioTime = 0
t = 0
last_midi = None

@win.event
def on_key_press(symbol, modifiers):
    global gameStarted
    global controlLabel
    
    if symbol == pyglet.window.key.ESCAPE:
        soundInput.stop()
        player.stop()
        win.close()
        sys.exit()
    
    if symbol == pyglet.window.key.SPACE and not gameStarted:
        gameStarted = True
        soundInput.start()
        controlLabel.x = -5000


notes = setupTrack(path=path)
timedMessages = buildTimedMessages(player.messages)
labelPlayingSong = objectCreator.createPlayingSongLabel(foreground)
labelYouSang = objectCreator.createSingNoteLabel(foreground)
controlLabel = objectCreator.createControlLabel(foreground)


def update(dt):
    global msg_index, timedMessages, audioTime, gameStarted, notes, t, gameEnded, last_midi, controlLabel
    t += dt

    if not gameStarted:
        return

    if gameStarted and not gameEnded:
        audioTime += dt  # ------ code based on generated code from chatGPT
        while (
            msg_index < len(timedMessages) and timedMessages[msg_index][0] <= audioTime
        ):
            _, msg = timedMessages[msg_index]
            if msg.type in ("note_on", "note_off"):
                player.playMessage(msg)
            msg_index += 1  # ----- end ChatGpt generated code

        for note in notes:
            note.rectangle.x = (win.width // 2 + 50) + (
                note.startTime - audioTime
            ) * 300

        # determine pitch for ptich rect height
        midi_note = (
            soundInput.freq_to_karaoke_midi()
        )  # midi note converison from ChatGPT

        # print("sung note: {}".format(midi_note))
        # print("freq:", soundInput.dominant_freq)
        # print("amp:", soundInput.amplitude)
        # print("dbfs:", soundInput.dbfs)

        if soundInput.dbfs < -42.5:
            midi_note = None

        if midi_note is not None:

            note = objectCreator.spawn_live_note(
                note=midi_note, time=0, group=foreground  # spawn at 0 point center line
            )
            sung_note_rects.append(note)

            last_midi = midi_note

        for sung_note_rect in sung_note_rects:
            sung_note_rect.x -= dt * 300

        if msg_index >= len(timedMessages):
            gameEnded = True
            controlLabel.text = 'Game Over Press ESC to exit the game'
            controlLabel.x = win.width//2
            
            

pyglet.clock.schedule_interval(update, 0.01)  # 100 per sec
pyglet.app.run()
