import mido, threading, sys
from mido import MidiFile
from scipy import signal


class MidiPlayer:
    def __init__(self):
        outports = mido.get_output_names()
        self.outport = mido.open_output(outports[0])
        self.messages = []
        self.playingThread = threading.Thread()

    def readFile(self, path):
        file = mido.MidiFile(path)
        for msg in file:
            self.messages.append(msg)

    def playMessage(self, message):
        self.outport.send(message)

    def stop(self):
        self.messages.clear()
        self.outport.close()
