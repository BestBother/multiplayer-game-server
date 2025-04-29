import socket
import pickle
import struct
import sys

try:
    PORT = int(sys.argv[1])
except (IndexError, ValueError):
    PORT = 9001  

HOST = '0.0.0.0' 


def physics_step(updates):
    new_positions = {}
    for pid, (x, y, vy, jumping) in updates.items():
        vy += 0.5  # gravity
        y  += vy
        # simple ground clamp at y=550
        if y > 550:
            y, vy, jumping = 550, 0, False
        new_positions[pid] = (x, y, vy, jumping)
    return new_positions

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"Physics worker listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_sock.accept()
        with conn:
            raw_len = recv_all(conn, 4)
            if not raw_len:
                continue
            msg_len = struct.unpack('!I', raw_len)[0]
            payload = recv_all(conn, msg_len)
            updates = pickle.loads(payload)
            result = physics_step(updates)
            out = pickle.dumps(result)
            print(f"[{HOST}:{PORT}] Processed {len(updates)} players")
            conn.sendall(struct.pack('!I', len(out)) + out)