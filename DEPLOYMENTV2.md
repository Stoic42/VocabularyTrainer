
### **词汇训练营 - 生产环境部署手册 (V2.0 增强版)**

#### **概述**

本文档详细说明了如何将“Lumi单词训练营”应用部署到一台全新的、基于`Ubuntu Server 22.04 LTS`的生产环境服务器上。

本部署方案采用业界标准的 **Nginx + Gunicorn + Flask** 架构，并通过`Systemd`进行进程守护，确保服务的稳定、高效和高可用。

-----

#### **1. 服务器环境准备 (在新服务器上执行)**

```bash
# 1.1 更新系统软件包列表并升级
sudo apt update && sudo apt upgrade -y

# 1.2 安装Python、pip及虚拟环境工具
sudo apt install python3 python3-pip python3-venv -y

# 1.3 安装Nginx
sudo apt install nginx -y

# 1.4 创建应用部署目录
# 推荐使用 /var/www/ 这个标准Web服务目录
sudo mkdir -p /var/www/vocabulary

# 1.5 将目录所有权赋予当前登录用户，方便后续上传文件
# 将 <your_username> 替换为您登录服务器的用户名，例如 ubuntu
sudo chown <your_username>:<your_username> /var/www/vocabulary
```

-----

#### **2. 上传应用文件**

此步骤分为两部分：用`git`拉取受版本控制的代码，和用`scp`上传不受版本控制的敏感文件。

```bash
# 2.1 进入部署目录
cd /var/www/vocabulary

# 2.2 从GitHub拉取代码
# 将 <your_branch_name> 替换为您要部署的、最新的稳定版分支或标签名，例如 v2.0.0
# 以下是具体的克隆和切换分支命令示例:

# 如果服务器上没有git，先安装git
sudo apt install git -y

# 从GitHub克隆代码
git clone https://github.com/Stoic42/vocabulary-trainer.git .
git checkout main  # 或使用最新的稳定版本号，如 v2.1.0, v2.2.0 等

# 2.3 【关键】上传被Git忽略的文件 (在您自己的本地电脑上执行)
# 使用 scp (Secure Copy) 命令，将您的“关键文件包”上传到服务器。
# scp -r [本地文件/文件夹路径] [服务器用户名]@[服务器IP地址]:[服务器目标路径]

# 示例：
# a. 上传数据库文件
scp C:\Users\YourUser\Desktop\deploy_package\vocabulary.db <your_username>@<your_server_ip>:/var/www/vocabulary/

# b. 上传配置文件模板
scp C:\Users\YourUser\Desktop\deploy_package\.env.prod.template <your_username>@<your_server_ip>:/var/www/vocabulary/

# c. 上传整个 wordlists 文件夹 (如果它被git忽略了)
scp -r C:\Users\YourUser\Desktop\deploy_package\wordlists <your_username>@<your_server_ip>:/var/www/vocabulary/
```

  * **提示**：如果您不熟悉`scp`命令，可以使用 **FileZilla** 或 **WinSCP** 这样的图形化SFTP工具，通过拖拽的方式上传文件，更加直观。

-----

#### **3. 应用环境配置 (回到服务器上执行)**

```bash
# 确保当前在 /var/www/vocabulary 目录下
cd /var/www/vocabulary

# 3.1 创建并激活Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3.2 安装所有依赖库
pip install -r requirements.txt
pip install gunicorn  # 确保gunicorn也被安装

# 3.3 创建并编辑生产环境的 .env 文件
cp .env.prod.template .env
nano .env  # 使用nano编辑器打开并填写您的配置
```

在 `.env` 文件中，请确保填写了服务器的真实配置，特别是**数据库的绝对路径**和**一个新的、极其复杂的`SECRET_KEY`**。
您可以通过以下方式生成一个安全的SECRET_KEY:


-----

#### **4. 配置并启动Gunicorn服务**

Gunicorn是专业的WSGI服务器，负责运行您的Python应用。

```bash
# 4.1 创建Gunicorn配置文件 (此文件定义了Gunicorn如何运行)
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
preload_app = True
chdir = "/var/www/vocabulary"
# Gunicorn的日志文件
accesslog = "/var/www/vocabulary/logs/gunicorn_access.log"
errorlog = "/var/www/vocabulary/logs/gunicorn_error.log"
# 应用入口，格式为 '模块名:应用实例'
wsgi_app = "app:app"
EOF

# 4.2 创建Systemd服务文件，让系统能管理Gunicorn
# 注意：User和Group设置为www-data，这是Nginx的默认运行用户，更安全
sudo tee /etc/systemd/system/vocabulary.service << EOF
[Unit]
Description=Gunicorn instance to serve Lumi Vocabulary Trainer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vocabulary
Environment="PATH=/var/www/vocabulary/venv/bin"
ExecStart=/var/www/vocabulary/venv/bin/gunicorn --config /var/www/vocabulary/gunicorn.conf.py

[Install]
WantedBy=multi-user.target
EOF

# 4.3 赋予Nginx用户对项目文件的访问权限
sudo chown -R www-data:www-data /var/www/vocabulary

# 4.4 启动并设置为开机自启
sudo systemctl daemon-reload
sudo systemctl start vocabulary
sudo systemctl enable vocabulary

# 4.5 检查服务状态
sudo systemctl status vocabulary
# (如果看到绿色的 "active (running)" 字样，说明Gunicorn已成功启动)
```

-----

#### **5. 配置Nginx反向代理**

Nginx是“大堂经理”，负责接待所有访客，并将他们引导到后台的Gunicorn服务。

```bash
# 5.1 创建Nginx站点配置文件
sudo tee /etc/nginx/sites-available/vocabulary << EOF
server {
    listen 80;
    listen [::]:80;
    server_name 82.157.204.20; # 【重要】替换为您的域名，或服务器公网IP

    location / {
        # 将所有请求转发给在8000端口运行的Gunicorn
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 为静态资源设置别名和缓存策略，提升性能
    location /assets/ {
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

# 5.2 启用这个站点配置
sudo ln -s /etc/nginx/sites-available/vocabulary /etc/nginx/sites-enabled/

# 5.3 测试Nginx配置是否有语法错误并重启
sudo nginx -t
sudo systemctl restart nginx
```

-----

#### **6. 防火墙与SSL证书（安全保障）**

```bash
# 6.1 配置防火墙，仅开放必要的端口
sudo ufw allow 'Nginx Full' # 开放HTTP (80) 和 HTTPS (443)
sudo ufw allow 'OpenSSH'   # 开放SSH (22)
sudo ufw enable            # 启用防火墙

# 6.2 (可选，但强烈推荐) 使用Certbot自动配置HTTPS
# 确保您的域名已经解析到了服务器IP
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com # 将your_domain.com替换为您的域名
```

至此，您的应用已经以专业、稳定且安全的方式成功部署到了生产环境！您可以随时通过“维护和监控”部分的命令来查看它的运行状态。


-----

#### **7. 故障排除与维护**

##### **常见问题解决**

**问题1：Unit vocabulary.service not found**
```bash
# 解决方案：重新创建systemd服务文件
sudo tee /etc/systemd/system/vocabulary.service << EOF
[Unit]
Description=Gunicorn instance to serve Lumi Vocabulary Trainer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vocabulary
Environment="PATH=/var/www/vocabulary/venv/bin"
ExecStart=/var/www/vocabulary/venv/bin/gunicorn --config /var/www/vocabulary/gunicorn.conf.py

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd并启动服务
sudo systemctl daemon-reload
sudo systemctl start vocabulary
sudo systemctl enable vocabulary
```

**问题2：权限错误**
```bash
# 解决方案：设置正确的文件权限
sudo chown -R www-data:www-data /var/www/vocabulary
sudo chmod -R 755 /var/www/vocabulary
sudo chmod 644 /var/www/vocabulary/vocabulary.db
```

**问题3：端口被占用**
```bash
# 检查端口占用情况
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80

# 如果端口被占用，可以修改gunicorn.conf.py中的bind地址
# 或者停止占用端口的服务
```

##### **服务状态检查**

```bash
# 检查Gunicorn服务状态
sudo systemctl status vocabulary

# 查看服务日志
sudo journalctl -u vocabulary -f

# 查看应用日志
tail -f /var/www/vocabulary/logs/app_*.log

# 查看Gunicorn日志
tail -f /var/www/vocabulary/logs/gunicorn_*.log

# 检查Nginx状态
sudo systemctl status nginx

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

##### **应用更新流程**

```bash
# 1. 停止服务
sudo systemctl stop vocabulary

# 2. 备份数据库
cp /var/www/vocabulary/vocabulary.db /var/www/vocabulary/vocabulary.db.backup.$(date +%Y%m%d_%H%M%S)

# 3. 更新代码（如果使用git）
cd /var/www/vocabulary
git pull origin main

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 5. 重启服务
sudo systemctl start vocabulary

# 6. 检查服务状态
sudo systemctl status vocabulary
```

##### **数据库备份**

```bash
# 创建备份脚本
cat > /var/www/vocabulary/backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/vocabulary"
mkdir -p \$BACKUP_DIR
cp /var/www/vocabulary/vocabulary.db \$BACKUP_DIR/vocabulary_\$(date +%Y%m%d_%H%M%S).db
# 保留最近30天的备份
find \$BACKUP_DIR -name "vocabulary_*.db" -mtime +30 -delete
EOF

chmod +x /var/www/vocabulary/backup.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
# 添加以下行：
# 0 2 * * * /var/www/vocabulary/backup.sh
```

##### **性能监控**

```bash
# 查看系统资源使用情况
htop
df -h
free -h

# 查看网络连接
netstat -tlnp

# 查看进程
ps aux | grep gunicorn
ps aux | grep nginx
```

-----

#### **8. 安全配置**

##### **更改默认密码**
```bash
# 首次部署后，请立即更改默认管理员密码
# 默认账户：admin / admin123
# 通过Web界面登录后修改密码
```

##### **生成安全的SECRET_KEY**
```bash
# 在服务器上生成安全的SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# 将生成的密钥更新到.env文件中
nano .env
```

##### **防火墙配置**
```bash
# 检查防火墙状态
sudo ufw status

# 只允许必要的端口
sudo ufw allow 'OpenSSH'
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

-----

#### **9. 访问应用**

部署完成后，您可以通过以下方式访问应用：

- **HTTP访问**：http://82.157.204.20
- **管理员登录**：用户名 `admin`，密码 `admin123`
- **首次登录后请立即修改默认密码**

##### **验证部署成功**

```bash
# 检查服务是否正常运行
curl http://127.0.0.1:8000

# 检查Nginx是否正常代理
curl http://82.157.204.20

# 查看服务状态
sudo systemctl status vocabulary
sudo systemctl status nginx
```

##### **HTTP 502错误故障排除**

如果访问网站时出现HTTP 502错误，说明Nginx正常工作但后端Gunicorn服务有问题。按以下步骤排查：

**步骤1：检查Gunicorn服务状态**
```bash
# 检查vocabulary服务状态
sudo systemctl status vocabulary

# 查看服务日志
sudo journalctl -u vocabulary -f
```

**步骤2：检查配置文件**
```bash
# 检查gunicorn配置文件是否存在
ls -la /var/www/vocabulary/gunicorn.conf.py

# 查看配置文件内容
cat /var/www/vocabulary/gunicorn.conf.py
```

**步骤3：检查应用文件**
```bash
# 检查app.py是否存在
ls -la /var/www/vocabulary/app.py

# 检查虚拟环境
ls -la /var/www/vocabulary/venv/bin/gunicorn
```

**步骤4：手动测试Gunicorn**
```bash
# 进入应用目录
cd /var/www/vocabulary

# 激活虚拟环境
source venv/bin/activate

# 手动启动Gunicorn测试
gunicorn --config gunicorn.conf.py app:app
```

**步骤5：检查端口占用**
```bash
# 检查8000端口是否被占用
sudo netstat -tlnp | grep :8000

# 检查80端口
sudo netstat -tlnp | grep :80
```

**步骤6：检查文件权限**
```bash
# 检查文件权限
sudo chown -R www-data:www-data /var/www/vocabulary
sudo chmod -R 755 /var/www/vocabulary
sudo chmod 644 /var/www/vocabulary/vocabulary.db
```

**常见问题解决：**

1. **端口问题**：应用运行在8000端口，通过Nginx代理到80端口
   - 直接访问：http://82.157.204.20:8000 （不推荐）
   - 通过Nginx：http://82.157.204.20 （推荐）

2. **favicon.ico缺失**：上传favicon文件
   ```bash
   # 在本地执行，上传favicon
   scp favicon.ico root@82.157.204.20:/var/www/vocabulary/
   ```

3. **服务启动失败**：检查日志中的具体错误信息
   ```bash
   # 查看详细错误日志
   sudo journalctl -u vocabulary -n 50
   ```