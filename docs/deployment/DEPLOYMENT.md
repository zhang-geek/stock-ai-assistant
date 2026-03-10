# A股AI助手 - 远程访问部署指南

## 方案一：Cloudflare Tunnel（推荐，免费）

### 安装 Cloudflare Tunnel
```bash
# Windows
winget install --id Cloudflare.cloudflared

# 或下载：https://github.com/cloudflare/cloudflared/releases
```

### 配置隧道
```bash
# 1. 登录 Cloudflare
cloudflared tunnel login

# 2. 创建隧道
cloudflared tunnel create stock-ai-assistant

# 3. 配置隧道（创建 config.yml）
# 见下方配置文件

# 4. 启动隧道
cloudflared tunnel run stock-ai-assistant
```

### config.yml 配置
```yaml
tunnel: <your-tunnel-id>
credentials-file: C:\Users\zhang\.cloudflared\<tunnel-id>.json

ingress:
  # 前端
  - hostname: stock-ai.your-domain.com
    service: http://localhost:5173

  # 后端 API
  - hostname: api.stock-ai.your-domain.com
    service: http://localhost:8000

  # 默认规则
  - service: http_status:404
```

### 启动服务
```bash
# 终端 1：启动后端
cd D:\development\projects\stock_personal
source .venv/Scripts/activate
uvicorn stock_assistant.api.main:app --host 0.0.0.0 --port 8000

# 终端 2：启动前端
cd frontend
npm run dev

# 终端 3：启动隧道
cloudflared tunnel run stock-ai-assistant
```

---

## 方案二：使用 ngrok（快速测试）

```bash
# 安装 ngrok
choco install ngrok

# 启动前端隧道
ngrok http 5173

# 启动后端隧道（另一个终端）
ngrok http 8000
```

---

## 方案三：部署到云服务器

### 使用 Docker Compose 部署

创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 部署到 VPS
```bash
# 1. 推送代码到服务器
git clone https://github.com/zhang-geek/stock-ai-assistant.git
cd stock-ai-assistant

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env

# 3. 启动服务
docker-compose up -d
```

---

## 方案四：前端部署到 Vercel

### 1. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 2. 部署前端
```bash
cd frontend
vercel --prod
```

### 3. 配置环境变量
在 Vercel 控制台设置：
- `VITE_API_URL`: 你的后端 API 地址

---

## 推荐方案组合

**开发/测试环境：**
- Cloudflare Tunnel（免费、稳定、支持自定义域名）

**生产环境：**
- 前端：Vercel（免费、CDN加速）
- 后端：云服务器（阿里云/腾讯云）+ Docker

---

## 安全建议

1. **启用认证**：添加用户登录功能
2. **HTTPS**：使用 SSL 证书
3. **API 限流**：防止滥用
4. **环境变量**：不要暴露 API Key
5. **防火墙**：限制访问 IP

---

## 监控和日志

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 监控资源使用
docker stats
```
