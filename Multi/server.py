# server.py
import socket
import threading
from multiprocessing import Process, Queue
import struct, time
from common import HOST, PORT, MSG_FMT, MSG_SIZE


clients = {}   
positions_lock = threading.Lock()
player_tags = {}

def physics_worker(task_q: Queue, result_q: Queue):
    while True:
        updates = task_q.get()
        if updates is None:
            break
        new_positions = {}
        for pid, (x, y, vy, jumping) in updates.items():
            vy += 0.5  # gravity
            y  += vy
            # simple ground clamp at y=550
            if y > 550:
                y, vy, jumping = 550, 0, False
            new_positions[pid] = (x, y, vy, jumping)
        result_q.put(new_positions)

def client_thread(conn, addr, pid, task_q: Queue, result_q: Queue):
    global positions
    buf = b''
    while True:
        while len(buf) < MSG_SIZE:
            data = conn.recv(1024)
            if not data:
                print(f"Disconnect: {pid}")
                return
            buf += data
        data, buf = buf[:MSG_SIZE], buf[MSG_SIZE:]
        _, x, y = struct.unpack(MSG_FMT, data)
        # update local state
        positions[pid] = (x, y, 0, False)
        # send current snapshot to physics process
        with positions_lock:
            positions[pid] = (x, y, 0, False)
            snapshot = positions.copy()

            task_q.put(snapshot)
            new_state = result_q.get()
            
        # broadcast to all clients
        packet = b''.join(struct.pack(MSG_FMT, p, *pos[:2]) for p, pos in new_state.items())
        for c, _ in clients.values():
            c.sendall(packet)

if __name__ == '__main__':
    task_q   = Queue()
    result_q = Queue()
    phys_p = Process(target=physics_worker, args=(task_q, result_q), daemon=True)
    phys_p.start()

    sock = socket.socket()
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
                args=(conn, addr, pid, task_q, result_q),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        pass
    finally:
        task_q.put(None)
        phys_p.join()
        sock.close()
