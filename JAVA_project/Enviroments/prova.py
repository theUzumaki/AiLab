import socket

sock = socket.socket()
sock.connect(("localhost", 8080))

sock1 = socket.socket()
sock1.connect(("localhost", 8080))

while True:
    continue