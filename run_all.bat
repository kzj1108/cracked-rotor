@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo pip install failed
    pause
    exit /b 1
)
echo.
echo Generating all figures...
python main.py --out output
if errorlevel 1 (
    echo run failed
    pause
    exit /b 1
)
echo.
echo Done. See folder: output
explorer output
pause
