import pyglet
from pyglet import window, display

# basend on WindowHandling Assignment 1
def setup_window(window):
    set_window_size_to_max(window)
    window.maximize()
    window.set_caption("Karaoke")


def set_window_size_to_max(window):
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    window.width = screen.width
    window.height = screen.height
