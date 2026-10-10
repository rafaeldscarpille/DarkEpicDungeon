# Capitão Scarpa (classe PIRATE): sprites animados

Fontes: `scripts/source/capitao-scarpa-folha-v2.png` (parado, ataque e morte) e `scripts/source/capitao-scarpa-andar-correr.png` (andar e correr, com as pernas alternando).

Cada animação fica em um PNG próprio. É uma tira horizontal de células de **128×128**, com fundo transparente. Os pés ficam na linha **y = 118** de cada célula.

**Padrão visual igual ao dos outros heróis:**
- altura de cerca de 68 px, escala 0.7 no jogo (mesma grade de pixel do Samurai e da Xamã);
- uma paleta única de 26 cores para todas as animações, clareada para combinar com o jogo;
- limpeza de pixels soltos e borda interna escurecida, que serve de contorno sem engrossar a silhueta.

| Arquivo | Quadros | Tamanho | Velocidade | Repete |
|---|---|---|---|---|
| `pirate_idle.png` | 4 | 512×128 | 4 fps | sim (um desenho só, respiração de 1 px) |
| `pirate_walk.png` | 8 | 1024×128 | 11 fps | sim |
| `pirate_run.png` | 8 | 1024×128 | 15 fps | sim |
| `pirate_attack.png` | 9 | 1152×128 | pelo tempo da arma (680 ms) | não |
| `pirate_death.png` | 8 | 1024×128 | 9 fps | não, fica no último |

O `pirate_config.json` traz os mesmos dados em formato de máquina: quadros, fps, de qual quadro da folha veio cada um e o mapa de estados.

## Como o jogo usa

O jogo não cria um sistema novo de animação. Ele usa o mesmo formato "pack" dos outros heróis:

- `scripts/build_pirate_sprites.py` gera as tiras acima e as junta na folha que o jogo carrega, `assets/pixel-art/characters/pirate-px1-body.png` (37 células) com `pirate-px1.json`. No JSON ficam o mapa de estados e as velocidades (`fps`).
- **Parado, andando e correndo** viram animações em loop (`mk4b-pirate-idle`, `-walk`, `-run`). Para ele correr, o direcional precisa estar inclinado acima de 62%, a mesma regra do jogo para todos os heróis. No teclado ele sempre corre.
- **Ataque:** a imagem acompanha as fases da arma, e o dano sai no fim da preparação, no tempo do jogo:
  - preparação (320 ms): quadros 0 (postura), 1 (prepara) e 2 (recua o sabre);
  - golpe (120 ms): quadros 3 (avança) e 4 (golpe amplo);
  - recuperação (240 ms): quadros 5 (extensão), 6 (continuação), 7 e 8 (volta à postura).

  O ataque não reinicia a cada atualização e, ao terminar, volta ao estado atual (parado, andando ou correndo).
- **Morte:** tem prioridade sobre tudo. Toca os 8 quadros uma vez e fica no último até o jogo remover o corpo.
- **Habilidades** usam quadros destas tiras. A Fúria Pirata usa a postura do ataque, um quadro de corrida para o salto e o golpe para baixo (ataque 6).
- Virar para a esquerda espelha o sprite, como em todos os heróis do jogo.

## Para corrigir ou trocar um quadro

1. Edite a folha de origem, ou troque a origem na tabela `ANIMS` do script.
2. Rode `python scripts/build_pirate_sprites.py`.
3. Se mudar a folha do jogo, troque o nome (`KEY` no script e o `"px1"` no `scripts/patch_pirate_class.py`). Sem isso, o cache offline do navegador continua mostrando a versão antiga.

## Andando e correndo

Vêm da folha própria `capitao-scarpa-andar-correr.png`: 2 linhas de 8 quadros, com as duas pernas alternando, gerada a partir do ciclo de referência (contato, apoio, passagem e impulso de cada perna). Os quadros entram na ordem desenhada, alinhados pelo quadril, com escala ajustada para o pirata ficar do mesmo tamanho das outras animações. A corrida mantém o sobe-e-desce e os quadros com os dois pés fora do chão.
