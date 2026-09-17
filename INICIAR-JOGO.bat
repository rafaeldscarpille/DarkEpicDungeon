@echo off
rem DEPTHGATE - inicia o servidor local de teste e abre o navegador.
rem Requisito: Node.js instalado (https://nodejs.org)
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js nao encontrado. Instale em https://nodejs.org e tente de novo.
  pause
  exit /b 1
)
node server.cjs
pause
