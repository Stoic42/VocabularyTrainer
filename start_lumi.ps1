# ======================================================
# 烛梦单词训练营 - PowerShell 启动脚本
# ======================================================

# 1. 设置当前窗口的标题，方便识别
$Host.UI.RawUI.WindowTitle = "烛梦单词服务器"

# 2. 打印提示信息
Write-Host "正在准备启动环境..." -ForegroundColor  Cyan

# 3. 激活您的 Conda 环境
# 为确保在任何位置都能正确激活，建议使用环境的完整路径
Write-Host "正在激活 Conda 环境 (VocabMVP)..."
conda activate C:\Users\wangq\conda_envs\VocabMVP

# 检查上一个命令是否成功执行
if ($? -ne $true ) {
    Write-Host "错误：Conda 环境激活失败！请检查路径是否正确。" -ForegroundColor  Red
    # 暂停，让用户可以看到错误信息
    Read-Host "按回车键退出"
    exit
}

Write-Host "环境激活成功！" -ForegroundColor  Green

# 4. 启动 Flask 应用程序
Write-Host "正在启动单词服务器 (app.py)..."
Write-Host "服务启动后，请不要关闭此窗口。" -ForegroundColor  Yellow
Write-Host "您可以随时在浏览器中访问 http://127.0.0.1:5000" -ForegroundColor  Yellow
Write-Host "--------------------------------------------------"

python app.py

# 5. （如果python app.py意外退出）保持窗口开启，方便查看错误日志
Write-Host "--------------------------------------------------"
Write-Host "服务器已停止运行。" -ForegroundColor  Magenta
Read-Host "按回车键关闭此窗口"