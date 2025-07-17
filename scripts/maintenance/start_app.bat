@echo off
echo === 词汇训练器启动脚本 ===
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已正确安装并添加到PATH
    pause
    exit /b 1
)

echo 正在清理日志文件...
REM 备份现有日志文件
if exist "logs\app.log" (
    set timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set timestamp=%timestamp: =0%
    move "logs\app.log" "logs\app.log.backup_%timestamp%"
    echo 已备份日志文件
)

REM 删除旧的备份文件
if exist "logs\app.log.*" (
    del "logs\app.log.*" /q
    echo 已清理旧备份文件
)

echo.
echo 正在启动应用...
echo 应用将在 http://127.0.0.1:5000 运行
echo 按 Ctrl+C 停止应用
echo.

REM 启动应用
python app.py

pause 