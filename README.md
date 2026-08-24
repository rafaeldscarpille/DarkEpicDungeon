# DarkEpicDungeon

DARK EPIC DUNGEONS — VERSÃO WEB (v1.1.0)
==========================================

COMO JOGAR
----------
Esta pasta contém o jogo completo em formato web estático.
Basta hospedar os arquivos em QUALQUER serviço de site estático e abrir
o endereço no navegador do celular (ou do computador).

Opções gratuitas e fáceis (arraste a pasta e pronto):
  1. Netlify Drop  →  https://app.netlify.com/drop
  2. GitHub Pages  →  suba os arquivos num repositório e ative o Pages
  3. Vercel        →  https://vercel.com
  4. itch.io       →  envie como "HTML game" (zip desta pasta)

Também funciona em qualquer servidor próprio (Apache, Nginx, IIS...):
copie os arquivos para a pasta pública do servidor. Pode ficar em
subpasta (ex.: meusite.com/jogos/ded/) — os caminhos são relativos.

IMPORTANTE
----------
- NÃO funciona abrindo o index.html direto do arquivo (file://).
  Precisa ser servido por um site (é limitação dos módulos JavaScript).
- Não é preciso instalar nada no celular. Não precisa de APK.

NO CELULAR (Android)
--------------------
- Jogue na HORIZONTAL (o jogo pede para virar o aparelho).
- Controles touch aparecem automaticamente: joystick virtual à esquerda,
  ataque (com arrastar para mirar), dash, 4 habilidades, interação,
  inventário e pausa à direita.
- Save automático no próprio navegador (localStorage).
- DICA: no Chrome, use o menu → "Adicionar à tela inicial" para instalar
  o jogo como aplicativo (PWA): abre em tela cheia, sem barra do navegador.

NO COMPUTADOR
-------------
- Teclado (WASD/setas + espaço/Shift), mouse e gamepad são suportados.
- Todas as teclas e botões são configuráveis em CONFIGURAÇÕES.

Desenvolvido por Rafael Scarpille.
