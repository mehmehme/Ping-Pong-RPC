==
      PROJETO PING PONG MULTIPLAYER - RPC & SOCKET
==

<div align="center">
<img src="https://media3.giphy.com/media/v1.Y2lkPTZjMDliOTUyeHdvem40ejQyZXQxOWd5NTlwMm44NTB4ZHVwNTl4OTdrY2dqMjc1eSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ECwTCTrHPVqKI/giphy.gif" width="500" height="300" />
</div>

Este projeto é um jogo de Ping Pong multiplayer desenvolvido em 
Python usando a biblioteca Pygame. O jogo utiliza uma arquitetura 
cliente-servidor (estilo RPC) para sincronização de movimentos, 
física autoritativa e gestão de latência.

--- ESTRUTURA DO PROJETO ---

1. constants.py        - Configurações de cores, tamanhos e rede.
2. net_manager.py      - Gerencia a conexão Socket entre Cliente/Servidor.
3. server.py           - O "Árbitro". Processa a física da bola e pontos.
4. main.py             - O Jogo. Trata interface, imagens e inputs.
5. latency_report.txt  - Log de rede gerado pelo Servidor.
6. client_latency_pX.txt - Relatório de latência gerado pelo Cliente.

--- REQUISITOS ---

* Python 3.x instalado.
* Biblioteca Pygame (Instale via: pip install pygame).
* Arquivos de imagem na mesma pasta:
    - praia.jpg (Fundo do jogo)
    - bola.jpg  (Sprite da bola)

--- COMO JOGAR ---

1. Inicie o SERVIDOR: 
   Abra um terminal e digite: python server.py

2. Inicie os CLIENTES:
   Abra outros dois terminais e em cada um digite: python main.py
   (O jogo aguardará ambos conectarem antes de iniciar).

--- FUNCIONALIDADES DE GESTÃO E REDE ---

* FÍSICA AUTORITATIVA: Para evitar trapaças e desync, a bola 
  só se move no servidor. O cliente apenas "desenha" o que recebe.
* CONTROLE DE CONCORRÊNCIA: Uso de threads para gerenciar 
  múltiplas conexões simultâneas.
* SINCRONISMO DE LARGADA: O servidor dita o tempo de contagem 
  regressiva para que ninguém comece com vantagem.
* LOG DE LATÊNCIA: O arquivo "client_latency_pX.txt" registra o 
  ping a cada 2 segundos para análise de performance.
* TRATAMENTO DE ERROS: Caso o servidor caia ou um jogador saia, 
  o sistema encerra a partida e gera um aviso.

--- COMANDOS ---

* MOUSE: Movimente o cursor para cima e para baixo para 
  controlar sua raquete.

Configuração de Rede: Para jogar em PCs diferentes, mude o 
"localhost" no net_manager.py para o IP do PC servidor.

