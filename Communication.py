import threading, wx

from serial import Serial

class Communicator:

    def __init__(self, tty, callback):
        self.callback = callback
        self.in_ = Serial(tty)
        self.out = Serial(tty)
        self.alive = True
        self.thread = threading.Thread(target=self._thread)
        self.thread.start()

    def _thread(self):
        getLine = self.in_.read_until
        while self.alive:
            line = getLine().rstrip()
            self.callback(line)

    def destroy(self):
        self.alive = False
        self.thread.join()

    def write(self, s):
        print >>self.out, s
