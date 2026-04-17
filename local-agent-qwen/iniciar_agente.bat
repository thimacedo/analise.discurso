@echo off
echo Baixando o modelo Qwen 2.5 Coder 7B...
ollama pull qwen2.5-coder:7b
echo.
echo Iniciando o Agente Local...
agent-local.exe
pause
