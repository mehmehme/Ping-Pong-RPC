import pygame
import sys
import time
from constants import *
from net_manager import Network

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong RPC")
font = pygame.font.SysFont("comicsans", 40)
score_font = pygame.font.SysFont("comicsans", 60)

bg_img = pygame.image.load("icons/praia.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

# Carrega a imagem da bola e estica para o tamanho definido (15x15)
ball_img = pygame.image.load("icons/voley.png").convert_alpha()
ball_img = pygame.transform.scale(ball_img, (BALL_SIZE, BALL_SIZE))

def draw_elements(game_state, player_id):
    """Função utilitária para desenhar o campo, raquetes, bola e placar"""
    win.blit(bg_img, (0, 0))
    pygame.draw.aaline(win, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    # Raquetes
    for i, p in enumerate(game_state["players"]):
        x_pos = 20 if i == 0 else WIDTH - 30
        pygame.draw.rect(win, WHITE, (x_pos, p["y"], PADDLE_WIDTH, PADDLE_HEIGHT))
    
    # Bola
    ball_pos = game_state["ball"]
    win.blit(ball_img, (ball_pos["x"], ball_pos["y"]))

    # Placar
    s0 = score_font.render(str(game_state["players"][0]["score"]), 1, WHITE)
    s1 = score_font.render(str(game_state["players"][1]["score"]), 1, WHITE)
    win.blit(s0, (WIDTH//4, 30))
    win.blit(s1, (3*WIDTH//4, 30))

def main():
    n = Network()
    if n.p is None:
        print("Erro: Servidor não encontrado.")
        return

    player_id = int(n.p)
    clock = pygame.time.Clock()
    # Gerenciamento do Relatório Local
    last_log_time = time.time()
    filename = f"client_latency_p{player_id}.txt"
    
    # Cria/Limpa o arquivo ao iniciar
    with open(filename, "w") as f:
        f.write(f"Relatório de Gestão de Latência - Jogador {player_id}\n")
        f.write("="*40 + "\n")
    while True:
        clock.tick(60)
        
        # 1. Entrada do usuário
        my_y = pygame.mouse.get_pos()[1] - PADDLE_HEIGHT // 2
        my_y = max(0, min(my_y, HEIGHT - PADDLE_HEIGHT)) # Trava na tela

        # 2. Comunicação com Servidor
        try:
            # Enviamos nossa posição e recebemos o estado autoritativo
            game_state = n.send({"y": my_y})
            if not game_state: break
        except:
            break

        # 3. Tratamento de Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # --- GESTÃO E LOG DE LATÊNCIA ---
        latency = game_state["players"][player_id]["latency"]
        
        # Grava no TXT a cada 2 segundos para não pesar o jogo
        current_time = time.time()
        if current_time - last_log_time > 2:
            with open(filename, "a") as f:
                timestamp = time.strftime("%H:%M:%S")
                f.write(f"[{timestamp}] Latência: {latency}ms | Concorrência: Ativa\n")
            last_log_time = current_time

        # 4. Lógica de Telas (Sincronizada pelo Servidor)
        num_ready = sum(1 for p in game_state["players"] if p.get("ready", False))
        
        if num_ready < 2:
            # Tela de Espera
            win.fill(BLACK)
            txt = font.render("Aguardando Oponente...", 1, WHITE)
            win.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
        
        elif not game_state.get("active", False):
            # Contagem Regressiva vinda do Servidor
            draw_elements(game_state, player_id)
            wait_val = game_state.get("wait_time", 0)
            msg = f"COMEÇANDO EM: {wait_val}" if wait_val > 0 else "VAI!"
            
            overlay = font.render(msg, 1, GREEN)
            win.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 + 50))
        
        else:
            # Jogo em Tempo Real
            draw_elements(game_state, player_id)

        pygame.display.update()

    # Finalização por desconexão
    win.fill(BLACK)
    msg = font.render("CONEXÃO PERDIDA!", 1, RED)
    win.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.delay(3000)

if __name__ == "__main__":
    main()