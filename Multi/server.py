import socket
import threading
import struct
import pickle
from common import HOST, PORT, MSG_FMT, MSG_SIZE

WORKER_NODES = [
    ('192.168.68.53', 9001),
]

positions = {}       
clients   = {}     
positions_lock = threading.Lock()

def call_worker(updates):
    global worker_index
    host, port = WORKER_NODES[worker_index]
    worker_index = (worker_index + 1) % len(WORKER_NODES)
    data = pickle.dumps(updates)
    print(f"worker", worker_index)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(struct.pack('!I', len(data)) + data)
        raw_len = sock.recv(4)
        resp_len = struct.unpack('!I', raw_len)[0]
        resp_payload = b''
        while len(resp_payload) < resp_len:
            resp_payload += sock.recv(resp_len - len(resp_payload))
    return pickle.loads(resp_payload)


def client_thread(conn, addr, pid):
    global positions
    buf = b''
    try:
        while True:
            while len(buf) < MSG_SIZE:
                data = conn.recv(1024)
                if not data:
                    raise ConnectionResetError 
                buf += data

            packet, buf = buf[:MSG_SIZE], buf[MSG_SIZE:]
            _, x, y = struct.unpack(MSG_FMT, packet)

            with positions_lock:
                positions[pid] = (x, y, 0.0, False)
                snapshot = positions.copy()

            new_state = call_worker(snapshot)

            out_packet = b''.join(
                struct.pack(MSG_FMT, p, *pos[:2])
                for p, pos in new_state.items()
            )

            dead_clients = []
            for c, _ in clients.values():
                try:
                    c.sendall(out_packet)
                except:
                    dead_clients.append(c)

            for dc in dead_clients:
                for dp, (dconn, _) in list(clients.items()):
                    if dconn == dc:
                        del clients[dp]
                        break

    except (ConnectionResetError, BrokenPipeError, socket.error):
        print(f"Disconnect: {pid}")
        with positions_lock:
            if pid in positions:
                del positions[pid]
            if pid in clients:
                del clients[pid]
        conn.close()

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    print(f"Server listening on {HOST}:{PORT}")

    next_pid = 1
    try:
        while True:
            conn, addr = sock.accept()
            pid = next_pid; next_pid += 1
            clients[pid] = (conn, addr)
            print(f"Client {pid} connected from {addr}")
            threading.Thread(
                target=client_thread,
                args=(conn, addr, pid),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
