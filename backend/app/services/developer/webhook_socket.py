import io
import socket
import time


class DeadlineReader(io.RawIOBase):
    def __init__(self, transport):
        self.transport = transport

    def readable(self):
        return True

    def readinto(self, buffer):
        self.transport.remaining()
        return self.transport.socket.recv_into(buffer)


class DeadlineSocket:
    def __init__(self, wrapped, deadline):
        self.socket, self.deadline = wrapped, deadline

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise socket.timeout('Webhook deadline exceeded')
        self.socket.settimeout(remaining)

    def makefile(self, mode):
        if mode != 'rb':
            raise ValueError('Webhook response is read-only')
        return io.BufferedReader(DeadlineReader(self))

    def sendall(self, data):
        self.remaining()
        self.socket.sendall(data)

    def close(self):
        self.socket.close()
