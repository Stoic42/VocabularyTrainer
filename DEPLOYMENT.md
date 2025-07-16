# 词汇训练营 - 生产环境部署指南

## 概述
本文档详细说明了如何将词汇训练营应用部署到生产环境。

## 环境要求
- Python 3.8+
- SQLite3
- 支持WSGI的Web服务器（如Nginx + Gunicorn）

## 部署步骤

### 1. 服务器环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 创建应用目录
sudo mkdir -p /var/www/vocabulary
sudo chown $USER:$USER /var/www/vocabulary
```

### 2. 上传应用文件

将以下文件上传到服务器：
- 所有Python源代码文件
- `requirements.txt`
- `config.prod.json`
- `.env.prod.template`
- `vocabulary.db`（包含学生数据的数据库文件）
- 所有静态资源文件（templates/, assets/, wordlists/等）

### 3. 环境配置

```bash
cd /var/www/vocabulary

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建生产环境配置文件
cp .env.prod.template .env
# 编辑 .env 文件，设置正确的生产环境配置
nano .env
```

### 4. 配置生产环境变量

编辑 `.env` 文件，确保包含以下配置：

```bash
# 生产环境配置
DATABASE_PATH=/var/www/vocabulary/vocabulary.db
LOG_LEVEL=INFO
LOG_DIR=/var/www/vocabulary/logs
AUDIO_DIR=/var/www/vocabulary/static/audio
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here
HOST=0.0.0.0
PORT=5000
FLASK_ENV=production
```

### 5. 设置文件权限

```bash
# 设置数据库文件权限
chmod 644 vocabulary.db

# 设置日志目录权限
mkdir -p logs
chmod 755 logs

# 设置应用目录权限
chmod 755 /var/www/vocabulary
```

### 6. 配置WSGI服务器

#### 使用Gunicorn

```bash
# 安装Gunicorn
pip install gunicorn

# 创建Gunicorn配置文件
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

#### 创建Systemd服务

```bash
sudo tee /etc/systemd/system/vocabulary.service << EOF
[Unit]
Description=Vocabulary Trainer Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vocabulary
Environment="PATH=/var/www/vocabulary/venv/bin"
ExecStart=/var/www/vocabulary/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable vocabulary
sudo systemctl start vocabulary
```

### 7. 配置Nginx反向代理

```bash
sudo tee /etc/nginx/sites-available/vocabulary << EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /var/www/vocabulary/assets/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /wordlists/ {
        alias /var/www/vocabulary/wordlists/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/vocabulary /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. 配置SSL（可选但推荐）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 9. 防火墙配置

```bash
# 允许HTTP和HTTPS流量
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 维护和监控

### 查看应用状态
```bash
# 查看服务状态
sudo systemctl status vocabulary

# 查看日志
sudo journalctl -u vocabulary -f

# 查看应用日志
tail -f /var/www/vocabulary/logs/app.log
```

### 更新应用
```bash
# 停止服务
sudo systemctl stop vocabulary

# 备份数据库
cp vocabulary.db vocabulary.db.backup.$(date +%Y%m%d_%H%M%S)

# 更新代码
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start vocabulary
```

### 数据库备份
```bash
# 创建备份脚本
cat > backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/vocabulary"
mkdir -p \$BACKUP_DIR
cp /var/www/vocabulary/vocabulary.db \$BACKUP_DIR/vocabulary_\$(date +%Y%m%d_%H%M%S).db
# 保留最近30天的备份
find \$BACKUP_DIR -name "vocabulary_*.db" -mtime +30 -delete
EOF

chmod +x backup.sh

# 添加到crontab
crontab -e
# 添加以下行（每天凌晨2点备份）：
# 0 2 * * * /var/www/vocabulary/backup.sh
```

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查日志：`sudo journalctl -u vocabulary -f`
   - 检查文件权限
   - 确认虚拟环境已激活

2. **数据库连接错误**
   - 检查数据库文件路径
   - 确认文件权限
   - 验证数据库文件完整性

3. **静态文件无法访问**
   - 检查Nginx配置
   - 确认文件路径正确
   - 检查文件权限

4. **性能问题**
   - 调整Gunicorn worker数量
   - 检查数据库查询性能
   - 监控服务器资源使用情况

## 安全注意事项

1. **更改默认密钥**
   - 修改 `.env` 文件中的 `SECRET_KEY`
   - 使用强密码生成器生成密钥

2. **文件权限**
   - 确保敏感文件不可公开访问
   - 限制数据库文件权限

3. **网络安全**
   - 配置防火墙
   - 使用HTTPS
   - 定期更新系统和依赖

4. **数据备份**
   - 定期备份数据库
   - 测试备份恢复流程

## 联系支持

如遇到部署问题，请检查：
1. 应用日志：`/var/www/vocabulary/logs/`
2. 系统日志：`sudo journalctl -u vocabulary`
3. Nginx日志：`/var/log/nginx/` 