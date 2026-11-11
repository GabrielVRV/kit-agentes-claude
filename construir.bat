@echo off
rem Gera dist\KitAgentesClaude.exe com o kit embutido, para usar em PCs sem Python.
setlocal
cd /d "%~dp0"

rem Com o painel aberto, o Windows nao deixa substituir o executavel.
tasklist /FI "IMAGENAME eq KitAgentesClaude.exe" | find /I "KitAgentesClaude.exe" >nul
if not errorlevel 1 (
    echo Feche o painel KitAgentesClaude.exe e rode de novo.
    exit /b 1
)

rem Ambiente virtual proprio: o PyInstaller nao entra no Python global.
if not exist .venv\Scripts\python.exe (
    python -m venv .venv || goto :erro
)
.venv\Scripts\python -m pip install --quiet --upgrade pyinstaller || goto :erro

rem Nao gera executavel se algum teste falhar.
.venv\Scripts\python -m unittest discover -s testes -t . || goto :erro

.venv\Scripts\pyinstaller --noconfirm --clean --onefile --windowed ^
    --name KitAgentesClaude ^
    --icon "painel\recursos\icone.ico" ^
    --add-data "claude-global;claude-global" ^
    --add-data "painel\recursos;painel\recursos" ^
    iniciar_painel.pyw || goto :erro

echo.
echo Pronto: dist\KitAgentesClaude.exe
exit /b 0

:erro
echo.
echo Falhou. Veja a mensagem acima.
exit /b 1
