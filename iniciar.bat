@echo off
set BASE_DIR=%~dp0
cd /d "%BASE_DIR%"
set PYTHONPATH=%BASE_DIR%
"C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe" src\cli\main.py %*
pause