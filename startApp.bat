setlocal
cd /d %~dp0
call env\Scripts\activate
call python main.py

pause