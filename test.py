import socket

HOST = '127.0.0.1'
PORT = 1006

print(f"Attempting to connect to {HOST}:{PORT}")
s = socket.socket()
s.settimeout(3)
s.connect((HOST, PORT))
print("Connected successfully!")
s.close()
