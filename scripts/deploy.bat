@echo off
:: Windows版本的部署脚本

echo 🚀 开始部署 NewZotero 应用...

:: 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

:: 切换到项目根目录
cd /d "%~dp0\.."

:: 停止现有容器（如果存在）
echo 🛑 停止现有容器...
docker-compose -f docker-compose.simple.yml down

:: 清理旧镜像（可选）
echo 🧹 清理旧镜像...
docker system prune -f

:: 构建并启动服务
echo 🏗️ 构建并启动服务...
docker-compose -f docker-compose.simple.yml up --build -d

:: 检查服务状态
echo 📊 检查服务状态...
docker-compose -f docker-compose.simple.yml ps

echo ✅ 部署完成！
echo 🌐 前端访问地址: http://localhost:3000
echo 🔧 后端API地址: http://localhost:5000

echo.
echo 📝 常用命令：
echo   查看日志: docker-compose -f docker-compose.simple.yml logs -f
echo   停止服务: docker-compose -f docker-compose.simple.yml down
echo   重启服务: docker-compose -f docker-compose.simple.yml restart

pause
