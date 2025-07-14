@echo off
echo ===================================
echo 修复单词"mess"显示为"mass"的问题
echo ===================================
echo.

echo 步骤1: 准备测试数据...
python test_fix_mess_display.py
echo.

echo 步骤2: 注入修复脚本...
python inject_fix_mess_display.py
echo.

echo 步骤3: 完成修复
echo 修复已完成，请重启应用并访问错误历史页面检查修复效果
echo 访问地址: http://localhost:5000/error-history
echo.

echo 如需了解更多信息，请查看 README_MESS_DISPLAY_FIX.md
echo.

pause