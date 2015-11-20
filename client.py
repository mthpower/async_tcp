# Echo client program
import socket
from time import sleep

HOST = ''                 # The remote host
PORT = 50007              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.sendall(b'Hello, world, 1\n')
data = s.recv(1024)
print('Received', repr(data))
sleep(2)

s.sendall(b'Hello, world, 2\n')
data = s.recv(1024)
print('Received', repr(data))
sleep(2)

s.sendall(b'Hello, world, 3\n')
data = s.recv(1024)
print('Received', repr(data))
sleep(2)

s.shutdown(socket.SHUT_RDWR)
s.close()
