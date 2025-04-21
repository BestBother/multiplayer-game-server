from multiprocessing import Process
import subprocess, time

def run_client():
    subprocess.run(['python', 'client.py'])

if __name__ == '__main__':
    for i in range(1, 10):
        print(f"Launching {i} clients...")
        clients = [Process(target=run_client) for _ in range(i)]
        for c in clients: c.start()
        time.sleep(10)  # Let them run for 10 sec
        for c in clients: c.terminate()
