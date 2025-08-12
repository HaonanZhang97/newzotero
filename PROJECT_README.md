# NewZotero - 知识库管理助手

一个基于Next.js + Flask的全栈知识管理系统，支持文档上传、笔记管理和智能搜索。

## 🏗️ 项目结构

```
newzotero/
├── frontend/                 # Next.js 前端应用
│   ├── src/                 # 源代码
│   ├── public/              # 静态资源
│   ├── package.json         # 前端依赖
│   └── Dockerfile           # 前端容器配置
│
├── backend/                  # Flask 后端API
│   ├── NewZotero_py.py     # Flask应用主文件
│   ├── requirements.txt     # Python依赖
│   └── Dockerfile          # 后端容器配置
│
├── scripts/                 # 部署和管理脚本
│   ├── deploy.sh           # Linux部署脚本
│   └── deploy.bat          # Windows部署脚本
│
├── docs/                    # 项目文档
│   └── DOCKER_README.md    # Docker部署详细说明
│
├── docker-compose.yml       # 完整版容器编排
├── docker-compose.simple.yml # 简化版容器编排
├── nginx.conf              # Nginx反向代理配置
└── README.md               # 本文件
```

## 🚀 快速启动

### 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone <your-repo-url>
cd newzotero

# 启动应用（简化版）
docker-compose -f docker-compose.simple.yml up -d

# 或启动完整版（包含Nginx）
docker-compose up -d
```

### 访问地址
- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:5000
- **Nginx代理**: http://localhost:80 (仅完整版)

## 🛠️ 开发环境

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python NewZotero_py.py
```

## 📚 功能特性

- ✅ **文档管理**: 支持PDF、DOCX文档上传和管理
- ✅ **笔记系统**: 摘录笔记和自由笔记双模式
- ✅ **智能搜索**: 基于语义相似度的内容搜索
- ✅ **DOI集成**: 自动获取学术文献信息
- ✅ **用户隔离**: 多用户数据隔离
- ✅ **文件下载**: 支持文件下载和管理

## 🐳 Docker部署

详细的Docker部署说明请查看 [Docker部署文档](docs/DOCKER_README.md)

### 快速部署命令
```bash
# Linux/Mac
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# Windows
scripts\deploy.bat
```

## 🔧 环境变量

创建 `.env` 文件：
```bash
# 应用配置
NODE_ENV=production
FLASK_ENV=production

# API配置
NEXT_PUBLIC_API_URL=http://localhost:5000

# 端口配置
FRONTEND_PORT=3000
BACKEND_PORT=5000
NGINX_PORT=80
```

## 📊 技术栈

### 前端
- **框架**: Next.js 15
- **语言**: JavaScript
- **样式**: CSS Modules
- **构建**: Docker

### 后端
- **框架**: Flask
- **语言**: Python 3.9
- **AI模型**: sentence-transformers (m3e-base)
- **搜索引擎**: Faiss
- **文件处理**: 支持PDF、DOCX

### 基础设施
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **数据存储**: JSON文件 + 文件系统

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v0.1.22
- ✨ 新增文件下载功能
- 🐛 修复Next.js 15异步参数问题
- 🔧 完善Docker部署配置
- 📚 新增详细文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

如果你遇到问题或有建议，请：
1. 查看 [文档](docs/)
2. 提交 [Issue](https://github.com/HaonanZhang97/newzotero/issues)
3. 加入讨论
