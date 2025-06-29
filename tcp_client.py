import os
import json
import socket
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

CHUNK_SIZE = 1024 #it is a power of 2 and lies between 512-2048 and small size would have caused too much packets and larger size would have caused risks to handle in udp and may be harder to handle 
HOST = '127.0.0.1'
PORT = 642
DATA_FOLDER = 'data'

KEY = b'Sixteen byte key' 

def encrypt_chunk(chunk, iv):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(chunk) + padder.finalize()
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()

def send_file(sock, filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    iv = os.urandom(16)

    meta = json.dumps({
        'filename': filename,
        'filesize': filesize,
        'iv': base64.b64encode(iv).decode()
    }).encode()

    sock.sendall(len(meta).to_bytes(4, 'big') + meta)

    sent = 0
    with open(filepath, 'rb') as f:
        while sent < filesize:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            encrypted_chunk = encrypt_chunk(chunk, iv)
            sock.sendall(len(encrypted_chunk).to_bytes(4, 'big') + encrypted_chunk)
            sent += len(chunk)

    print(f"[\u2713] Encrypted & Sent '{filename}' ({filesize} bytes)")

def main():
    files = [
        os.path.join(DATA_FOLDER, fname)
        for fname in os.listdir(DATA_FOLDER)
        if os.path.isfile(os.path.join(DATA_FOLDER, fname))
    ]
    print(f"[+] Sending folder '{DATA_FOLDER}' with {len(files)} files")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        count_str = str(len(files)).ljust(16)
        sock.sendall(count_str.encode())

        for path in files:
            print(f"[>] Sending '{os.path.basename(path)}'")
            send_file(sock, path)

if __name__ == '__main__':
    main()