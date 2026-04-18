# e:\PROJETO ÓDIO POLÍTICA\local-agent-qwen\iniciar_agente.ps1

Write-Host "=== Iniciando Ambiente do Agente Qwen 2.5 ===" -ForegroundColor Cyan

# 1. Verifica se o Ollama está rodando
$ollamaCheck = Get-Process ollama -ErrorAction SilentlyContinue
if (!$ollamaCheck) {
    Write-Host "[!] Ollama não detectado. Iniciando..." -ForegroundColor Yellow
    # Tenta iniciar o Ollama
    try {
        Start-Process "ollama" "serve" -WindowStyle Hidden
        Write-Host "[+] Aguardando inicialização do Ollama (5s)..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
    } catch {
        Write-Host "[!] Erro ao iniciar Ollama automático. Certifique-se de que o Ollama está instalado." -ForegroundColor Red
    }
}

# 2. Garante o modelo correto
Write-Host "[>] Verificando modelo qwen2.5-coder:7b..." -ForegroundColor Gray
ollama pull qwen2.5-coder:7b

# 3. Executa o Agente
if (Test-Path ".\agent-local.exe") {
    Write-Host "[+] Agente Ativado. Pronto para comandos." -ForegroundColor Green
    .\agent-local.exe
} else {
    Write-Host "[!] Erro: agent-local.exe não encontrado nesta pasta." -ForegroundColor Red
    Write-Host "[i] Caminho atual: $(Get-Location)"
}
