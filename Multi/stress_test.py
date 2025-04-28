# stress_test.py
import socket, struct, threading, time, random
from common import HOST, PORT, MSG_FMT

def fake_client(pid):
    try:
        sock = socket.socket()
        sock.connect((HOST, PORT))

        x, y = random.randint(100, 600), 100.0
        while True:
            x += random.uniform(-5, 5)
            y += random.uniform(-2, 2)  

            msg = struct.pack(MSG_FMT, pid, x, y)
            sock.sendall(msg)
            time.sleep(1 / 60.0)  
    except Exception as e:
        print(f"[Fake {pid}] Error:", e)

# Start a bunch of clients
if __name__ == '__main__':
    NUM_FAKE_CLIENTS = 50  
    for pid in range(1000, 1000 + NUM_FAKE_CLIENTS):
        threading.Thread(target=fake_client, args=(pid,), daemon=True).start()

    while True:
        time.sleep(1) 
