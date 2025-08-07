@echo off
chcp 65001 >nul 2>&1
title bilibili-ai-partition 构建脚本

echo.
echo ========================================
echo   bilibili-ai-partition 构建脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

REM 运行构建脚本
echo.
echo 🔧 开始构建...
python build.py

if errorlevel 1 (
    echo.
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo.
echo 🎉 构建成功完成！
echo 📁 可执行文件位于 release\ 目录
echo.
pause
