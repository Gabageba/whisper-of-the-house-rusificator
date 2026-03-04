@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Запуск через -c и runpy обходит ассоциацию .py файлов
py -u -c "import runpy; runpy.run_path(r'extract_english_keys.py', run_name='__main__')"

if errorlevel 1 (
    echo.
    echo Script failed. Press any key to close.
    pause >nul
    exit /b 1
)
echo.
pause
