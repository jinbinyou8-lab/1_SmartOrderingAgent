@echo off
chcp 65001 >nul
setlocal EnableExtensions
echo ========================================
echo    AiMenu 智能点餐系统 - 前端启动
echo ========================================
echo.

echo 正在检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js环境正常

echo.
echo 正在检查依赖包...
if not exist "node_modules" (
    echo 📦 首次运行，正在安装依赖包...
    npm install
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖包已存在
)

echo.
echo 🚀 正在启动开发服务器...
echo 📝 前端地址: http://localhost:3000
echo 📝 确保后端API运行在: http://localhost:8000
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

npm run dev

pause 
