@echo off
call conda activate C:\Users\wangq\conda_envs\VocabMVP
start python app.py
ping 127.0.0.1 -n 5 >nul
start http://127.0.0.1:5000
pause