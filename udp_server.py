# udp_server.py

import socket
import os
import json
import base64

CHUNK_SIZE = 1024
HOST = '0.0.0.0'
PORT = 1006
SAVE_FOLDER = 'received_data_udp'

buffers = {}
expected_chunks = {}

os.makedirs(SAVE_FOLDER, exist_ok=True)

def handle_packet(packet):
    if packet.get('done'):
        filename = packet['filename']
        buffer = buffers.pop(filename, {})
        total = expected_chunks.pop(filename, len(buffer))
        save_path = os.path.join(SAVE_FOLDER, filename)
        if os.path.exists(save_path):
            print(f"[!] File '{filename}' already exists. Overwriting...")
        with open(save_path, 'wb') as f:
            for seq in range(total):
                if seq in buffer:
                    f.write(buffer[seq])
                else:
                    print(f"[!] Missing chunk {seq} for file '{filename}' — incomplete.")
                    return
        print(f"[✓] Received '{filename}' ({total} chunks)")
        return
    try:
        filename = packet['filename']
        seq = packet['seq']
        total = packet['total']
        chunk_data = base64.b64decode(packet['data'])
        if filename not in buffers:
            buffers[filename] = {}
            expected_chunks[filename] = total
        buffers[filename][seq] = chunk_data
    except Exception as e:
        print("[!] Failed to decode packet:", e)
def main():
    print(f"[+] UDP server listening on port {PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        while True:
            data, addr = sock.recvfrom(CHUNK_SIZE + 1024)
            try:
                packet = json.loads(data.decode())
                handle_packet(packet)
            except Exception as e:
                print("[!] Invalid packet received:", e)

if __name__ == '__main__':
    main()
