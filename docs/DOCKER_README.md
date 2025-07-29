# NewZotero Docker 部署指南

## 🚀 快速开始

### 1. 安装 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加用户到docker组（避免使用sudo）
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 安装 Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 部署应用
```bash
# 方法1: 使用部署脚本（推荐）
chmod +x deploy.sh
./deploy.sh

# 方法2: 手动部署
docker-compose up --build -d
```

## 📁 项目结构
```
newzotero/
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile             # Next.js 前端 Dockerfile
├── nginx.conf            # Nginx 配置
├── deploy.sh             # Linux 部署脚本
├── deploy.bat            # Windows 部署脚本
├── backend/              # Flask 后端
│   ├── Dockerfile        # Flask Dockerfile
│   ├── requirements.txt  # Python 依赖
│   └── NewZotero_py.py  # Flask 应用
└── src/                 # Next.js 源代码
```

## 🛠️ 常用命令

### 基本操作
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看运行状态
docker-compose ps
```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f nginx
```

### 进入容器
```bash
# 进入前端容器
docker-compose exec frontend sh

# 进入后端容器
docker-compose exec backend bash

# 进入Nginx容器
docker-compose exec nginx sh
```

### 数据管理
```bash
# 查看数据卷
docker volume ls

# 备份数据
docker run --rm -v newzotero_backend_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .

# 恢复数据
docker run --rm -v newzotero_backend_uploads:/data -v $(pwd):/backup alpine tar xzf /backup/uploads-backup.tar.gz -C /data
```

## 🌐 访问地址

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:5000
- **Nginx代理**: http://localhost:80

## 🔧 生产环境配置

### 1. 域名配置
编辑 `nginx.conf` 文件：
```nginx
server_name your-domain.com;  # 替换为你的域名
```

### 2. SSL证书配置
```bash
# 创建SSL目录
mkdir ssl

# 将证书文件放入ssl目录
# ssl/cert.pem
# ssl/key.pem

# 取消nginx.conf中HTTPS配置的注释
```

### 3. 环境变量配置
创建 `.env` 文件：
```bash
# 生产环境配置
NODE_ENV=production
FLASK_ENV=production

# API地址配置
NEXT_PUBLIC_API_URL=http://backend:5000

# 其他配置
PORT=3000
```

## 🐛 故障排除

### 端口占用问题
```bash
# 查看端口占用
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80

# 停止占用端口的进程
sudo kill -9 <PID>
```

### 权限问题
```bash
# 修复Docker权限
sudo chown -R $USER:$USER .
sudo chmod -R 755 .
```

### 镜像构建失败
```bash
# 清除构建缓存
docker builder prune -a

# 重新构建镜像
docker-compose build --no-cache
```

### 数据持久化问题
```bash
# 检查数据卷
docker volume inspect newzotero_backend_uploads

# 清理未使用的数据卷（谨慎使用）
docker volume prune
```

## 📊 监控和维护

### 资源使用情况
```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df
```

### 自动重启配置
在 `docker-compose.yml` 中已配置 `restart: unless-stopped`，确保容器异常退出后自动重启。

### 日志轮转
```bash
# 限制日志大小（在docker-compose.yml中添加）
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "3"
```

## 🔄 更新部署

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 重新构建并部署
docker-compose up --build -d
```

### 滚动更新
```bash
# 逐个重启服务，避免服务中断
docker-compose up -d --no-deps frontend
docker-compose up -d --no-deps backend
```

## 📞 技术支持

如果遇到问题，可以：
1. 查看日志：`docker-compose logs -f`
2. 检查服务状态：`docker-compose ps`
3. 重启服务：`docker-compose restart`
4. 清理环境：`docker-compose down && docker system prune -f`
