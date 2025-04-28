import pygame, socket, threading, struct
from common import HOST, PORT, MSG_FMT, MSG_SIZE

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Multiplayer Client")


sock = socket.socket()
sock.connect((HOST, PORT))

player_id = None
x, y = W//2, H-100
vy = 0
jumping = False
positions = {}   # other players

def recv_loop():
    global positions
    buf = b''
    while True:
        data = sock.recv(1024)
        if not data: break
        buf += data
        # (pid, x, y)
        while len(buf) >= MSG_SIZE:
            pid, px, py = struct.unpack(MSG_FMT, buf[:MSG_SIZE])
            buf = buf[MSG_SIZE:]
            positions[pid] = (px, py)


threading.Thread(target=recv_loop, daemon=True).start()

clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  x -= 5
    if keys[pygame.K_RIGHT]: x += 5
    if keys[pygame.K_SPACE] and not jumping:
        vy, jumping = -10, True

    vy += 0.5
    y += vy
    if y > H-50:
        y, vy, jumping = H-50, 0, False


    sock.sendall(struct.pack(MSG_FMT, player_id or 0, x, y))

   
    screen.fill((255,255,255))

    pygame.draw.rect(screen, (0,0,255), (x,y,50,50))
 
    for pid, (px,py) in positions.items():
        if pid != player_id:
            pygame.draw.rect(screen, (0,255,0), (px,py,50,50))
    pygame.display.flip()

pygame.quit()
sock.close()
