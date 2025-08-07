@echo off
chcp 65001 >nul 2>&1
title 项目清理工具

echo.
echo ========================================
echo   bilibili-ai-partition 项目清理
echo ========================================
echo.

REM 运行Python清理脚本
python clean.py

if errorlevel 1 (
    echo.
    echo ❌ 清理过程中出现错误
    pause
    exit /b 1
)

echo.
echo 🎉 项目清理完成！
echo.
pause
