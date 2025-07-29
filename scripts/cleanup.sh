#!/bin/bash
echo "🧹 清理旧文件..."

# 删除根目录的旧前端文件
rm -rf src public node_modules .next

# 删除旧的配置文件
rm -f package.json package-lock.json next.config.mjs postcss.config.mjs jsconfig.json Dockerfile

# 删除旧的环境文件
rm -f .env

echo "✅ 清理完成！"
echo "📁 新的项目结构："
echo "  frontend/     - 前端应用"
echo "  backend/      - 后端应用"
echo "  scripts/      - 部署脚本"
echo "  docs/         - 项目文档"
echo ""
echo "🚀 现在可以使用以下命令启动："
echo "  docker-compose -f docker-compose.simple.yml up -d"
echo ""
