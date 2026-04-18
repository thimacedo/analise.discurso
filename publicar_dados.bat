@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo  Publicador automatico - Politica com Lupa
echo ==================================================

if not exist ".venv\Scripts\activate" (
    echo [ERRO] Ambiente virtual nao encontrado.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Falha ao ativar o ambiente virtual.
    pause
    exit /b 1
)

echo [OK] Ambiente virtual ativado.

echo.
echo [1/5] Sincronizando perfis seguidos do Instagram...
python atualizar_perfis.py
if errorlevel 1 (
    echo [AVISO] Falha ao sincronizar perfis. Usando lista anterior...
)

echo.
echo [2/5] Executando pipeline de coleta e analise...
python orquestrador.py
if errorlevel 1 (
    echo [ERRO] Pipeline falhou.
    pause
    exit /b 1
)

echo.
echo [3/5] Localizando o CSV mais recente...
for /f "delims=" %%i in ('dir /b /od resultado_*.csv 2^>nul') do set LATEST=%%i
if "%LATEST%"=="" (
    echo [ERRO] Nenhum arquivo resultado_*.csv encontrado.
    pause
    exit /b 1
)
echo Arquivo encontrado: %LATEST%

echo.
echo [4/5] Copiando para api/dados_latest.csv...
copy "%LATEST%" "api\dados_latest.csv" /Y

echo.
echo [5/5] Enviando para o GitHub...
git add api\dados_latest.csv perfis_monitorados.json
git commit -m "Atualiza dados reais da analise - %date% %time%"
if errorlevel 1 (
    echo [AVISO] Nada para commitar.
) else (
    git push origin main
)

echo.
echo ==================================================
echo  SUCESSO! Dados publicados.
echo ==================================================
pause
