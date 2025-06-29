import socket
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

CHUNK_SIZE = 1024 + 16  # ciphertext may be longer due to padding so gave littile extra bytes
HOST = '0.0.0.0'
PORT = 642
SAVE_FOLDER = 'received_data'

KEY = b'Sixteen byte key' 

def decrypt_chunk(chunk, iv):
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(chunk) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

def recv_exact(conn, size):
    buf = b''
    while len(buf) < size:
        data = conn.recv(size - len(buf))
        if not data:
            raise ConnectionError("Connection lost during recv_exact")
        buf += data
    return buf

def receive_file(conn):
    meta_len_bytes = recv_exact(conn, 4)
    meta_len = int.from_bytes(meta_len_bytes, 'big')
    meta = recv_exact(conn, meta_len).decode()
    info = json.loads(meta)

    filename = info['filename']
    filesize = info['filesize']
    iv = base64.b64decode(info['iv'])

    os.makedirs(SAVE_FOLDER, exist_ok=True)
    save_path = os.path.join(SAVE_FOLDER, filename)

    if os.path.exists(save_path):
        print(f"[!] File '{filename}' already exists. Overwriting...")

    decrypted_bytes = 0
    with open(save_path, 'wb') as f:
        while decrypted_bytes < filesize:
            try:
                len_bytes = recv_exact(conn, 4)
                chunk_len = int.from_bytes(len_bytes, 'big')
                encrypted_chunk = recv_exact(conn, chunk_len)

                decrypted_chunk = decrypt_chunk(encrypted_chunk, iv)
                to_write = decrypted_chunk[:min(len(decrypted_chunk), filesize - decrypted_bytes)]
                f.write(to_write)
                decrypted_bytes += len(to_write)
            except Exception as e:
                print(f"[!] Decryption failed: {e}")
                break

    print(f"[✓] Decrypted & Received '{filename}' ({filesize} bytes)")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"[+] TCP server listening on port {PORT}")

        conn, addr = server.accept()
        with conn:
            print(f"[<] Connection from {addr}")
            header = conn.recv(16).decode().strip()
            try:
                file_count = int(header)
            except ValueError:
                print("[!] Invalid file count header. Closing.")
                return

            for _ in range(file_count):
                receive_file(conn)

if __name__ == '__main__':
    main()