import platform
import threading
import queue
import os
import socket
import select
import sys


class ConnectionClosedError(Exception):
    pass


class SocketTimeoutError(Exception):
    pass


class PosixConsole:
    def __init__(self, channel, inputfile):
        self.channel = channel
        self.inputfile = inputfile

    def run(self):
        import termios
        import tty

        localtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            self.channel.settimeout(0)

            while True:
                read, write, exception = select.select([self.channel, sys.stdin], [], [])

                if self.channel in read:
                    try:
                        data = self.channel.recv(256)
                        if len(data) == 0:
                            raise ConnectionClosedError()
                        sys.stdout.write(data.decode("utf-8", errors="ignore"))
                        sys.stdout.flush()
                    except socket.timeout as e:
                        raise SocketTimeoutError(e)

                if sys.stdin in read:
                    data = sys.stdin.read(1)
                    if len(data) == 0:
                        raise ConnectionClosedError()
                    self.channel.send(data)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, localtty)


class WindowsConsole:
    TYPE_KEYBOARD_INPUT = 0
    TYPE_TERMINAL_OUTPUT = 1
    TYPE_REMOTE_CLOSED = 2
    TYPE_SOCKET_TIMEOUT = 3

    class KeyboardInputThread(threading.Thread):
        def __init__(self, queue):
            super(KeyboardInputThread, self).__init__()
            self.daemon = True
            self.queue = queue

        def run(self):
            while True:
                ch = sys.stdin.read(1)
                self.queue.put((KEYBOARD_INPUT_DATA, ch))

    class TerminalOutputThread(threading.Thread):
        def __init__(self, queue, channel):
            super(TerminalOutputThread, self).__init__()
            self.daemon = True
            self.queue = queue
            self.channel = channel

        def run(self):
            while True:
                try:
                    data = self.channel.recv(256)
                    if len(data) == 0:
                        self.queue.put((TYPE_REMOTE_CLOSED, None))
                        break
                    data = data.decode("utf-8", errors="ignore")
                    self.queue.put((TYPE_TERMINAL_OUTPUT, data))
                except socket.timeout:
                    self.queue.put((TYPE_SOCKET_TIMEOUT, None))
                    break

    def __init__(self, channel, inputfile):
        self.channel = channel
        self.dataQueue = queue.Queue()
        self.inputThread = KeyboardInputThread(self.dataQueue)
        self.outputThread = TerminalOutputThread(self.dataQueue, self.channel)

    def run(self):
        self.inputThread.start()
        self.outputThread.start()

        while True:
            dataType, data = self.queue.get()

            if dataType == TYPE_KEYBOARD_INPUT:
                channel.send(data)
            if dataType == TYPE_TERMINAL_OUTPUT:
                sys.stdout.write(data)
                sys.stdout.flush()
            if dataType == TYPE_REMOTE_CLOSED:
                raise ConnectionClosedError()
            if dataType == TYPE_SOCKET_TIMEOUT:
                raise SocketTimeoutError()


class Console:
    def __init__(self, channel, inputfile):
        if os.name == 'nt':
            self._console = WindowsConsole(channel, inputfile)
        else:
            self._console = PosixConsole(channel, inputfile)

    def run(self):
        return self._console.run()
