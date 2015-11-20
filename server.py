# Echo server program
from select import select
import socket

HOST = ''
PORT = 50007

# Sockets are not meant to be inherited, so we have to key into this by
# file descriptor number to be able to get retrieve the BufferedSocket.
SOCKETS = {}


class BufferedSocket(object):

    """Wrapper around a socket to hold a "buffer"."""

    buffer = b''
    closed = False

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.fileno = sock.fileno()

    @property
    def readable(self):
        read, _, __ = select([self.sock], [], [], 0)
        return bool(read)

    @property
    def writeable(self):
        _, write, __ = select([], [self.sock], [], 0)
        return bool(write)

    @property
    def has_error(self):
        _, __, error = select([], [], [self.sock], 0)
        return bool(error)

    def receive(self):
        # Read until we would block
        while self.readable:
            chunk = self.sock.recv(4096)
            # Check to see if the socket has been closed.
            if chunk == b'':
                self.closed = True
                break

            self.buffer += chunk

    def echo(self):
        # Write until we would block and
        # as long as we can see a newline, keep sending.
        while self.writeable and b'\n' in self.buffer:
            position = self.buffer.find(b'\n')
            msg = self.buffer[:position + 1]
            sent = self.send(msg)
            # Check to see if the client has disconnected
            if sent == 0:
                self.closed = True
                break

            self.buffer = self.buffer[sent:]

    def send(self, msg):
        sent = self.sock.send(msg)
        return sent

    def close(self):
        print('Disconnected: ', self.addr)
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.closed = True


def accept(socket):
    """Accept a new connection."""
    conn, addr = socket.accept()
    print('Connected: ', addr)
    return BufferedSocket(sock=conn, addr=addr)


def read_loop(sockets):
    """
    Loop over readable sockets and see if we
    can do any work on them in turn.
    """
    for sock in sockets:
        buff_sock = SOCKETS[sock.fileno()]
        buff_sock.receive()


def write_loop(sockets):
    """
    Loop over writeable sockets and see if we
    can do any work on them in turn.
    """
    for sock in sockets:
        buff_sock = SOCKETS[sock.fileno()]
        buff_sock.echo()


def closed():
    """Handle closed sockets and remove them from the loop."""
    closed = [sock for sock in SOCKETS.values() if sock.closed]
    for sock in closed:
        sock.close()
        SOCKETS.pop(sock.fileno)


def create_server_socket():
    """Special case to create our server socket and have it listen."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    return server


def main_loop(server):
    server_fileno = server.fileno()
    while True:
        # Grab all the sockets we know about
        read = write = [s.sock for s in SOCKETS.values()]

        # Add our server socket to the read list
        read += [server]

        # Block here until *something* is ready to read from
        readable, _, __ = select(read, [], [])

        # First see if we can accept a new connection
        readable_descriptors = [sock.fileno() for sock in readable]
        # Is our server in the readable sockets list?
        if server_fileno in readable_descriptors:
            # accept and add the new connection to our sockets loop
            new_sock = accept(server)
            SOCKETS.update({new_sock.fileno: new_sock})

        # Regardless of whether we accepted a new connection,
        # poll (timeout=0) to see what we can work on.
        read = write = [s.sock for s in SOCKETS.values()]
        readable, writeable, _ = select(read, write, [], 0)

        read_loop(readable)
        write_loop(writeable)
        closed()


if __name__ == '__main__':
    server = create_server_socket()
    try:
        main_loop(server)

    except KeyboardInterrupt:
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        for sock in SOCKETS.values():
            sock.close()
