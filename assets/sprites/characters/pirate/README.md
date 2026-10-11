# Capitão Scarpa (classe PIRATE): sprites animados

Fontes: `scripts/source/pirata-separados/` (parado, andando, correndo e atacando: 8 quadros cada, 222×444 com fundo transparente, todos na mesma tela) e `scripts/source/capitao-scarpa-folha-v3.png` (só a morte, que não veio nos quadros separados). Os quadros separados ficam na posição em que foram desenhados na tela comum, então o sobe-e-desce e o avanço do golpe são os do artista. Pedaços do quadro vizinho que vieram no recorte são removidos.

Cada animação fica em um PNG próprio. É uma tira horizontal de células de **128×128**, com fundo transparente. Os pés ficam na linha **y = 118** de cada célula.

**Padrão visual igual ao dos outros heróis** (medido nas folhas deles):
- altura de cerca de 68 px com o contorno, escala 0.7 no jogo e pés na linha 118;
- desenhado por **materiais**, como os outros: couro (casaco, cabelo e botas), pele, faixa vermelha, dourado, camisa/lâmina e calça. Cada material tem de 1 a 4 tons, tirados da paleta comum dos heróis (cerca de 20 cores no total);
- cada pixel da arte em alta resolução é classificado num material. Na redução, detalhes pequenos (dourado, camisa, faixa, pele, linhas escuras) têm prioridade sobre o couro, para não sumirem na média;
- os tons vêm do brilho suavizado: áreas chapadas, sem o "chuvisco" da arte pintada. Pixels soltos são limpos;
- contorno de 1 px por fora na cor (5,4,3), a mesma de todos os outros heróis.

| Arquivo | Quadros | Tamanho | Velocidade | Repete |
|---|---|---|---|---|
| `pirate_idle.png` | 8 | 1024×128 | 6 fps | sim |
| `pirate_walk.png` | 8 | 1024×128 | 11 fps | sim |
| `pirate_run.png` | 8 | 1024×128 | 14 fps | sim |
| `pirate_attack.png` | 8 | 1024×128 | pelo tempo da arma (680 ms) | não |
| `pirate_death.png` | 8 | 1024×128 | 9 fps | não, fica no último |

O `pirate_config.json` traz os mesmos dados em formato de máquina: quadros, fps, de qual quadro da folha veio cada um e o mapa de estados.

## Como o jogo usa

O jogo não cria um sistema novo de animação. Ele usa o mesmo formato "pack" dos outros heróis:

- `scripts/build_pirate_sprites.py` gera as tiras acima e as junta na folha que o jogo carrega, `assets/pixel-art/characters/pirate-sep1-body.png` (40 células) com `pirate-sep1.json`. No JSON ficam o mapa de estados e as velocidades (`fps`).
- **Parado, andando e correndo** viram animações em loop (`mk4b-pirate-idle`, `-walk`, `-run`). Para ele correr, o direcional precisa estar inclinado acima de 62%, a mesma regra do jogo para todos os heróis. No teclado ele sempre corre.
- **Ataque:** a imagem acompanha as fases da arma, e o dano sai no fim da preparação, no tempo do jogo:
  - preparação (320 ms): quadros 0 (postura), 1 (prepara) e 2 (recua o sabre);
  - golpe (120 ms): quadros 3 (desce) e 4 (corte, lâmina inteira);
  - recuperação (240 ms): quadros 5 (continuação) e 7 (volta à postura). O quadro 6 ergue o sabre para um 2º golpe e fica de fora do golpe simples.

  O ataque não reinicia a cada atualização e, ao terminar, volta ao estado atual (parado, andando ou correndo).
- **Morte:** tem prioridade sobre tudo. Toca os 8 quadros uma vez e fica no último até o jogo remover o corpo.
- **Habilidades** usam quadros destas tiras. A Fúria Pirata usa a postura do ataque, um quadro de corrida para o salto e o corte (ataque 4).
- Virar para a esquerda espelha o sprite, como em todos os heróis do jogo.

## Para corrigir ou trocar um quadro

1. Edite a folha de origem, ou troque a origem na tabela `ANIMS` do script.
2. Rode `python scripts/build_pirate_sprites.py`.
3. Se mudar a folha do jogo, troque o nome (`KEY` no script e o `"sep1"` no `scripts/patch_pirate_class.py`). Sem isso, o cache offline do navegador continua mostrando a versão antiga.

## Andando e correndo

Vêm das pastas `andando` e `correndo`, na ordem dos arquivos, na mesma escala do parado (pirata em pé ≈ 372 px na origem).
