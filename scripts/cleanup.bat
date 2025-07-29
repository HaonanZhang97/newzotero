@echo off
echo 🧹 清理旧文件...

:: 删除根目录的旧前端文件
if exist "src" rmdir /s /q "src"
if exist "public" rmdir /s /q "public"
if exist "node_modules" rmdir /s /q "node_modules"
if exist ".next" rmdir /s /q ".next"

:: 删除旧的配置文件
if exist "package.json" del "package.json"
if exist "package-lock.json" del "package-lock.json"
if exist "next.config.mjs" del "next.config.mjs"
if exist "postcss.config.mjs" del "postcss.config.mjs"
if exist "jsconfig.json" del "jsconfig.json"
if exist "Dockerfile" del "Dockerfile"

:: 删除旧的环境文件
if exist ".env" del ".env"

echo ✅ 清理完成！
echo 📁 新的项目结构：
echo   frontend/     - 前端应用
echo   backend/      - 后端应用  
echo   scripts/      - 部署脚本
echo   docs/         - 项目文档
echo.
echo 🚀 现在可以使用以下命令启动：
echo   docker-compose -f docker-compose.simple.yml up -d
echo.
pause
