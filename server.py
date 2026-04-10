import socket
from _thread import *
from constants import *
import time
import json
import pygame

server = "0.0.0.0"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((server, port))
except socket.error as e:
    print(f"Erro ao iniciar servidor: {e}")

s.listen(2)
print("Servidor Online. Aguardando jogadores...")

# --- CLASSE DA BOLA (Lógica no Servidor) ---
class ServerBall:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y

    def update(self, p0_y, p1_y):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

        p0_rect = pygame.Rect(20, p0_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        p1_rect = pygame.Rect(WIDTH - 30, p1_y, PADDLE_WIDTH, PADDLE_HEIGHT)

        if self.rect.colliderect(p0_rect) or self.rect.colliderect(p1_rect):
            self.speed_x *= -1

        point = [0, 0]
        if self.rect.left <= 0:
            point[1] = 1 # Ponto P2
            self.reset()
        elif self.rect.right >= WIDTH:
            point[0] = 1 # Ponto P1
            self.reset()
        return point

    def reset(self):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.speed_x *= -1

# --- ESTADO GLOBAL E CONTROLE ---
ball_instance = ServerBall()
pos = [
    {"y": 250, "score": 0, "latency": 0, "ready": False}, 
    {"y": 250, "score": 0, "latency": 0, "ready": False}
]
curr_player = 0
start_game_time = 0

def game_logic_thread():
    """Thread independente para processar a física da bola"""
    global pos, start_game_time
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        if curr_player == 2:
            if start_game_time == 0:
                start_game_time = time.time() + 3
            
            if time.time() > start_game_time:
                points = ball_instance.update(pos[0]["y"], pos[1]["y"])
                pos[0]["score"] += points[0]
                pos[1]["score"] += points[1]
        else:
            start_game_time = 0 # Reset se alguém sair

def threaded_client(conn, player):
    """Gerencia a comunicação individual de cada jogador"""
    global pos, curr_player, start_game_time
    conn.send(str.encode(str(player)))
    pos[player]["ready"] = True

    while True:
        try:
            start_tick = time.perf_counter()
            data = conn.recv(2048).decode('utf-8')
            if not data: break
            
            received = json.loads(data)
            pos[player]["y"] = received["y"]

            # Latência e Relatório
            latency = round((time.perf_counter() - start_tick) * 1000, 2)
            pos[player]["latency"] = latency
            
            if int(time.time()) % 15 == 0: # Log a cada 15s
                with open("latency_report.txt", "a") as f:
                    f.write(f"P{player} Ping: {latency}ms | {time.ctime()}\n")

            # Pacote de resposta sincronizado
            wait_time = max(0, int(start_game_time - time.time())) if start_game_time != 0 else 3
            game_state = {
                "players": pos,
                "ball": {"x": ball_instance.rect.x, "y": ball_instance.rect.y},
                "wait_time": wait_time,
                "active": (time.time() > start_game_time) if start_game_time != 0 else False
            }
            conn.sendall(str.encode(json.dumps(game_state)))
        except:
            break

    print(f"Jogador {player} saiu.")
    curr_player -= 1
    pos[player]["ready"] = False
    pos[player]["score"] = 0
    ball_instance.reset()
    conn.close()

# Inicia a física antes do loop de conexões
start_new_thread(game_logic_thread, ())

while True:
    conn, addr = s.accept()
    if curr_player < 2:
        print(f"Conectado a: {addr}")
        start_new_thread(threaded_client, (conn, curr_player))
        curr_player += 1
    else:
        conn.close() # Recusa se já houver 2