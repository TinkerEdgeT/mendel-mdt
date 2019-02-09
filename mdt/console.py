import os
import platform
import queue
import select
import socket
import sys
import threading


class ConnectionClosedError(Exception):
    def __init__(self, exit_code=None):
        self.exit_code = exit_code


class SocketTimeoutError(Exception):
    pass


class PosixConsole:
    def __init__(self, channel, inputfile):
        self.channel = channel
        self.inputfile = inputfile

    def run(self):
        import termios
        import tty

        localtty = None
        try:
            localtty = termios.tcgetattr(self.inputfile)
        except termios.error as e:
            pass

        try:
            if localtty:
                tty.setraw(self.inputfile.fileno())
                tty.setcbreak(self.inputfile.fileno())

            self.channel.settimeout(0)

            while True:
                read, write, exception = select.select([self.channel, self.inputfile], [], [])

                if self.channel in read:
                    try:
                        data = self.channel.recv(256)
                        if len(data) == 0:
                            exit_code = None
                            if self.channel.exit_status_ready():
                                exit_code = self.channel.recv_exit_status()
                            raise ConnectionClosedError(exit_code=exit_code)
                        sys.stdout.write(data.decode("utf-8", errors="ignore"))
                        sys.stdout.flush()
                    except socket.timeout as e:
                        raise SocketTimeoutError(e)

                if self.inputfile in read:
                    data = self.inputfile.read(1)
                    if len(data) == 0:
                        exit_code = None
                        if self.channel.exit_status_ready():
                            exit_code = self.channel.recv_exit_status()
                        raise ConnectionClosedError(exit_code=exit_code)
                    self.channel.send(data)
        finally:
            if localtty:
                termios.tcsetattr(self.inputfile, termios.TCSADRAIN, localtty)


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
                        exit_code = None
                        if self.channel.exit_status_ready():
                            exit_code = self.channel.recv_exit_status()
                        self.queue.put((TYPE_REMOTE_CLOSED, exit_code))
                        break
                    data = data.decode("utf-8", errors="ignore")
                    self.queue.put((TYPE_TERMINAL_OUTPUT, data))
                except socket.timeout:
                    self.queue.put((TYPE_SOCKET_TIMEOUT, None))
                    break

            exit_status = self.channel.recv_exit_status()
            self.queue.put((TYPE_EXIT_CODE, exit_status))

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
                raise ConnectionClosedError(exit_code=data)
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
