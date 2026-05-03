import pyglet, math
from pyglet import sprite, image


class ObjectCreator:
    def __init__(self, window, batch):
        self.window = window
        self.batch = batch
        self.y_sec = self.window.height // 10
        self.x_sec = self.window.width // 12

    def createLines(self, group):
        lines = []
        line_h = pyglet.shapes.Line(
            x=self.window.width // 2.5,
            y=self.y_sec * 2,
            x2=self.window.width - self.x_sec,
            y2=self.y_sec * 2,
            thickness=2,
            color=(255, 255, 255),
            batch=self.batch,
            group=group,
        )
        lines.append(line_h)

        line_v = pyglet.shapes.Line(
            x=self.window.width // 2,
            y=self.y_sec * 9,
            x2=self.window.width // 2,
            y2=self.y_sec * 1,
            thickness=2,
            color=(255, 255, 255),
            batch=self.batch,
            group=group,
        )
        lines.append(line_v)

        return lines

    def createPitchRectangle(self, group):
        rect = pyglet.shapes.Rectangle(
            x=self.window.width // 2,
            y=self.window.height // 2,
            width=self.x_sec * 0.25,
            height=self.y_sec * 0.5,
            color=(0, 255, 0),
            batch=self.batch,
            group=group,
        )
        rect.x -= rect.width//2
        rect.y -= rect.height//2 # center the thing like anchor in middle
        return rect
    
    def setObjectYFromNoteHelper(self, object, note):
            # 55 lowest note and 67 highest
            min_note = 52  # little bit extra for other files
            max_note = 70
            normalized = (note - min_note) / (max_note - min_note)
            bottom_line = 2 * self.y_sec
            total_space = 6 * self.y_sec
            object.y = bottom_line + total_space * normalized
            
    def createNoteRectangles(
        self, midiMessages, group
    ):  # this method was fixed using Lumo AI assistant
        # AI changed the method from working on matching based on iterating through lists to using an active note dict
        # hier noch einfügen das immer nur ein ton aktiv sein kann
        noteRects = []
        rectangles = []

        # Dictionary to hold active notes: { note_number: NoteRect_instance }
        active_notes = {}

        current_time = 0

        # Single pass through all messages
        for msg in midiMessages:
            # Update cumulative time (Delta Time approach)
            current_time += msg.time

            if msg.type == "note_on" and msg.velocity > 0:
                # 1. Create the NoteRect
                newNoteRect = self.NoteRect(batch=self.batch, group=group, creator=self)
                newNoteRect.setX1FromStartTime(current_time)
                newNoteRect.setNote(msg.note)

                # 2. Store it in the dictionary so we can find it later
                # If the same note is played again while still holding, this overwrites.
                # For simple visualizers, this is usually fine.
                active_notes[msg.note] = newNoteRect
                noteRects.append(newNoteRect)

            elif msg.type == "note_off" or (
                msg.type == "note_on" and msg.velocity == 0
            ):
                # 3. Check if we have an active note to close
                if msg.note in active_notes:
                    note_rect = active_notes.pop(msg.note)  # Remove from active

                    # 4. Set the width based on the duration
                    note_rect.setWidthFromEndTime(current_time)

                    # 5. Create the final graphic and add to list
                    rect = note_rect.create()
                    rectangles.append(rect)
        return noteRects

    class NoteRect:
        def __init__(self, batch, group, creator):
            self.x1 = None
            self.width = None
            self.startTime = None
            self.duration = None
            self.y = None
            self.color = (255, 0, 0)
            self.note = None
            self.batch = batch
            self.group = group
            self.creator = creator
            self.rectangle = None

        def setX1FromStartTime(self, startTime):
            self.startTime = startTime
            self.x1 = math.floor(float(startTime) * 500) + (
                self.creator.window.width // 2
            )  # start center line of the window

        def setWidthFromEndTime(self, endTime):
            self.duration = endTime - self.startTime
            self.width = math.floor(self.duration * 500)

        def setNote(self, note):
            self.note = note
            self.setYFromNote(note)

        def setYFromNote(self, note):
            self.creator.setObjectYFromNoteHelper(self,note)

        def create(self):
            w = max(1, self.width)

            rect = pyglet.shapes.Rectangle(
                x=self.x1,
                y=self.y,
                width=self.width,
                height=self.creator.y_sec // 5,
                color=self.color,
                batch=self.batch,
                group=self.group,
            )
            self.rectangle = rect
            return rect
