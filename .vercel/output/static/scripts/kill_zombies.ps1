# [STN-X01] Zombie Process Killer (PowerShell version)
# Destrói processos zumbis nas portas 8000/8080

Write-Host "🧟 Caçador de Zumbis ativado..." -ForegroundColor Cyan

$ports = @(8000, 8080)

foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
    if ($process) {
        Stop-Process -Id $process -Force
        Write-Host "Zumbis na porta $port eliminados." -ForegroundColor Green
    } else {
        Write-Host "Porta $port limpa." -ForegroundColor Yellow
    }
}

Write-Host "✅ Ambiente de dev desbloqueado." -ForegroundColor Green
