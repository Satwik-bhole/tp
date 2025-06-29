import socket
import os
import json
import math
import base64
import time
CHUNK_SIZE = 1024
HOST = '127.0.0.1'  # IP of the server
PORT = 1006
DATA_FOLDER = 'data'

def send_udp_file(sock, filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    total_chunks = math.ceil(filesize / CHUNK_SIZE)
    print(f"[>] Sending '{filename}' in {total_chunks} chunks")
    with open(filepath, 'rb') as f:
        for seq in range(total_chunks):
            chunk = f.read(CHUNK_SIZE)
            encoded_data = base64.b64encode(chunk).decode()
            packet = {
                'filename': filename,
                'seq': seq,
                'total': total_chunks,
                'data': encoded_data
            }
            sock.sendto(json.dumps(packet).encode(), (HOST, PORT))
            time.sleep(0.001) #small delay between packets to avoid them getting lost 
    done_packet = {
        'filename': filename,
        'done': True
    }
    sock.sendto(json.dumps(done_packet).encode(), (HOST, PORT))
    print(f"[✓] Finished sending '{filename}'")
def main():
    files = [
        os.path.join(DATA_FOLDER, fname)
        for fname in os.listdir(DATA_FOLDER)
        if os.path.isfile(os.path.join(DATA_FOLDER, fname))
    ]
    print(f"[+] Sending folder '{DATA_FOLDER}' with {len(files)} files")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for filepath in files:
            send_udp_file(sock, filepath)

if __name__ == '__main__':
    main()
