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

:: 停止现有容器（如果存在）
echo 🛑 停止现有容器...
docker-compose down

:: 清理旧镜像（可选）
echo 🧹 清理旧镜像...
docker system prune -f

:: 构建并启动服务
echo 🏗️ 构建并启动服务...
docker-compose up --build -d

:: 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

echo ✅ 部署完成！
echo 🌐 前端访问地址: http://localhost:3000
echo 🔧 后端API地址: http://localhost:5000
echo 🌍 Nginx代理地址: http://localhost:80

echo.
echo 📝 常用命令：
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo   进入容器: docker-compose exec [服务名] sh

pause
