# Multi-File Transfer over TCP and UDP
## Implementation Overview
This project implements two file transfer systems:
1. TCP-based transfer for reliable streaming
2. UDP-based transfer for datagram transmission with packet management

Both systems transfer entire folders with any file type while handling overwrites, metadata transmission, and progress logging.

## TCP Implementation (tcp_server.py/tcp_client.py)
Protocol Characteristics:  
- Stream-oriented reliable transfer
- In-order delivery guarantee

Workflow:
1. Client:
   - Scans `data/` folder and sends file count (16-byte header)
   - For each file:
     - Sends JSON metadata (filename + filesize)
     - Streams file in 1024-byte chunks
     - Logs overwrite warnings
2. Server:
   - Receives file count header
   - Creates `received_data/` directory
   - Processes files sequentially:
     - Checks for existing files (logs overwrites)
     - Reconstructs files from chunks

Key Features:
- Fixed 1024-byte chunk size (optimal balance between overhead and performance)
- File existence checks with overwrite warnings
- Robust error handling for invalid headers

## UDP Implementation (udp_server.py/udp_client.py)
Protocol Characteristics:  
- Datagram-based transmission
- Handles packet ordering and loss detection

Workflow:
1. Client:
   - Splits files into 1024-byte chunks
   - For each chunk:
     - Sends JSON packet with:
       - Base64-encoded data
       - Sequence number
       - Total chunks
       - Filename
   - Sends `{"done": true}` packet after all chunks
   - Includes 1ms delay between packets to reduce loss
2. Server:
   - Buffers out-of-order packets using sequence numbers
   - On "done" signal:
     - Reassembles chunks in order
     - Reports missing chunks
     - Writes file with overwrite warnings

Key Features:
- Base64 encoding for safe binary transfer
- Sequence numbering for packet reassembly
- Missing chunk detection
- Fixed 1024-byte chunks (prevents UDP fragmentation issues)

---

## Additional Feature: Base64 Encoding (UDP)
- Purpose: Safely transmit binary files in JSON packets
- Implementation:
  - Client encodes raw bytes to base64 strings
  - Server decodes back to binary
- Benefit: Prevents data corruption during JSON serialization of binary files

## Additional Feature: AES Encryption (TCP)

Feature: End-to-end encryption using AES-128 (CBC mode) for TCP file transfer.

## Implementation Details:
- A 16-byte shared key (`KEY = b'Sixteen byte key'`) is used on both client and server.
- For each file:
  - Client generates a random IV and sends it in metadata (base64-encoded).
  - Each file chunk is encrypted using AES with PKCS7 padding.
  - Each encrypted chunk is sent with a 4-byte length prefix.
  - Server decrypts chunk-by-chunk using the same IV and key.

## Benefits:
- Ensures confidentiality of transferred files
- Demonstrates understanding of secure file transfer principles
- Introduced with minimal overhead using standard libraries (`cryptography`)

## Additional Feature: Base64 Encoding (UDP)

Purpose: Safely transmit binary files within JSON packets over UDP.

## Implementation:
- Each file chunk is encoded using `base64.b64encode()` before being sent.
- The server decodes using `base64.b64decode()` before reconstruction.

## Benefit:
- Prevents JSON corruption from binary control characters
- Ensures full binary compatibility for all file types (images, PDFs, etc.)

## Issues Faced
1. UDP Packet Loss:
   - Mitigated with 1ms inter-packet delays(packets were lost or duplicated)
2. Binary File Corruption (UDP):
   - Solved with base64 encoding
