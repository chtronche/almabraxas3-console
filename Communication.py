import threading

from serial import Serial

class Communicator:

    def __init__(self, tty, callback):
        self.callback = callback
        self.in_ = Serial(tty, 115200)
        self.out = Serial(tty, 115200)
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
        self.out.write(bytes(s, 'iso-8859-15'))
        self.out.write(b'\n')
