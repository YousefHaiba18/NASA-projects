import socket

mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

mainSocket.bind(('127.0.0.1', 80))

mainSocket.listen(1)