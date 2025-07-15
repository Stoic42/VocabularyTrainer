# 词汇训练营 - 生产环境更新指南 (V3.0)

## 概述

本文档专门用于处理已经部署的生产环境的代码更新和数据库同步，避免推倒重来，采用优雅的增量更新方式。

## 适用场景

- 生产环境已经部署，但代码版本较旧
- 需要获取最新的稳定版本代码
- 需要同步最新的数据库文件
- 环境配置（.env、Nginx、systemd等）已经配置好

## 更新策略

### 方案一：优雅更新（推荐）

#### 1. 备份当前环境

```bash
# 进入应用目录
cd /var/www/vocabulary

# 备份当前代码和配置
sudo cp -r . ../vocabulary_backup_$(date +%Y%m%d_%H%M%S)

# 备份数据库
sudo cp vocabulary.db ../vocabulary.db.backup.$(date +%Y%m%d_%H%M%S)

# 备份配置文件
sudo cp .env ../.env.backup.$(date +%Y%m%d_%H%M%S)
```

#### 2. 安装git（如果没有）

```bash
# 检查git是否已安装
git --version

# 如果没有安装，则安装git
sudo apt install git -y
```

#### 3. 初始化git仓库并拉取最新代码

```bash
# 解决git权限问题（如果遇到"dubious ownership"错误）
git config --global --add safe.directory /var/www/vocabulary

# 设置正确的文件所有权
sudo chown -R root:root /var/www/vocabulary
sudo chown -R www-data:www-data /var/www/vocabulary/logs
sudo chown www-data:www-data /var/www/vocabulary/vocabulary.db

# 如果目录不是git仓库，初始化它
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/Stoic42/vocabulary-trainer.git
    git fetch origin
    git checkout -b main origin/main
else
    # 如果已经是git仓库，直接拉取更新
    git fetch origin
    git reset --hard origin/main
fi

# 查看当前版本
git log --oneline -5
```

#### 4. 恢复配置文件

```bash
# 恢复.env文件（如果被覆盖了）
if [ ! -f ".env" ]; then
    sudo cp ../.env.backup.* .env
fi

# 确保.env文件存在且有正确配置
if [ ! -f ".env" ]; then
    cp .env.prod.template .env
    echo "请手动编辑.env文件，设置正确的配置"
    nano .env
fi
```

#### 5. 更新依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt
pip install gunicorn

# 检查依赖是否安装成功
pip list | grep -E "(Flask|gunicorn|gTTS)"
```

#### 6. 同步最新数据库

在**本地电脑**上执行：

```bash
# 上传最新的数据库文件
scp vocabulary.db root@82.157.204.20:/var/www/vocabulary/

# 上传favicon（如果需要）
scp favicon.ico root@82.157.204.20:/var/www/vocabulary/
```

在**服务器**上执行：

```bash
# 设置数据库文件权限
sudo chmod 644 /var/www/vocabulary/vocabulary.db
sudo chown www-data:www-data /var/www/vocabulary/vocabulary.db
```

#### 7. 重启服务

```bash
# 设置文件权限
sudo chown -R www-data:www-data /var/www/vocabulary
sudo chmod -R 755 /var/www/vocabulary

# 重启服务
sudo systemctl restart vocabulary

# 检查服务状态
sudo systemctl status vocabulary

# 测试应用
curl http://127.0.0.1:8000
```

### 方案二：完全重建（如果方案一失败）

#### 1. 备份重要文件

```bash
# 备份当前环境
cd /var/www/vocabulary
sudo cp -r . ../vocabulary_backup_$(date +%Y%m%d_%H%M%S)
```

#### 2. 清理并重新克隆

```bash
# 清空目录（保留备份）
sudo rm -rf * .*

# 重新克隆
git clone https://github.com/Stoic42/vocabulary-trainer.git .

# 切换到main分支
git checkout main
```

#### 3. 重新配置环境

```bash
# 重新创建虚拟环境
sudo rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 恢复.env配置
sudo cp ../vocabulary_backup_*/vocabulary_backup_*/.env .

# 上传最新数据库
# （在本地执行：scp vocabulary.db root@82.157.204.20:/var/www/vocabulary/）

# 重新创建服务配置
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
preload_app = True
chdir = "/var/www/vocabulary"
accesslog = "/var/www/vocabulary/logs/gunicorn_access.log"
errorlog = "/var/www/vocabulary/logs/gunicorn_error.log"
wsgi_app = "app:app"
EOF

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart vocabulary
```

## 验证更新

### 1. 检查代码版本

```bash
# 查看git提交历史
git log --oneline -10

# 查看当前分支
git branch -a
```

### 2. 检查服务状态

```bash
# 检查Gunicorn服务
sudo systemctl status vocabulary

# 检查Nginx服务
sudo systemctl status nginx

# 查看服务日志
sudo journalctl -u vocabulary -f
```

### 3. 测试应用功能

```bash
# 测试本地访问
curl http://127.0.0.1:8000

# 测试公网访问
curl http://82.157.204.20

# 在浏览器中访问
# http://82.157.204.20
```

## 故障排除

### 常见问题

**问题1：git pull冲突**
```bash
# 解决冲突
git stash
git pull origin main
git stash pop
```

**问题2：依赖安装失败**
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt
```

**问题3：服务启动失败**
```bash
# 查看详细错误
sudo journalctl -u vocabulary -n 50

# 手动测试应用
cd /var/www/vocabulary
source venv/bin/activate
python app.py
```

**问题4：数据库权限问题**
```bash
# 修复权限
sudo chown www-data:www-data vocabulary.db
sudo chmod 644 vocabulary.db
```

**问题5：Git权限问题**
```bash
# 如果遇到"dubious ownership in repository"错误
git config --global --add safe.directory /var/www/vocabulary

# 或者重新设置文件所有权
sudo chown -R root:root /var/www/vocabulary
sudo chown -R www-data:www-data /var/www/vocabulary/logs
sudo chown www-data:www-data /var/www/vocabulary/vocabulary.db

# 如果还有问题，可以重新初始化git仓库
sudo rm -rf .git
git init
git remote add origin https://github.com/Stoic42/vocabulary-trainer.git
git fetch origin
git checkout -b main origin/main
```

## 回滚方案

如果更新后出现问题，可以快速回滚：

```bash
# 停止服务
sudo systemctl stop vocabulary

# 恢复备份
sudo cp -r ../vocabulary_backup_*/* .
sudo cp ../vocabulary.db.backup.* vocabulary.db

# 重启服务
sudo systemctl start vocabulary

# 检查状态
sudo systemctl status vocabulary
```

## 最佳实践

1. **定期备份**：每次更新前都要备份
2. **测试环境**：先在测试环境验证更新
3. **分步更新**：代码更新和数据库更新分开进行
4. **监控日志**：更新后密切监控服务日志
5. **回滚准备**：确保有快速回滚方案

## 自动化脚本

可以创建更新脚本来自动化这个过程：

```bash
#!/bin/bash
# update_vocabulary.sh

set -e

echo "开始更新词汇训练营..."

# 备份
echo "备份当前环境..."
cd /var/www/vocabulary
sudo cp -r . ../vocabulary_backup_$(date +%Y%m%d_%H%M%S)

# 更新代码
echo "更新代码..."
git fetch origin
git reset --hard origin/main

# 更新依赖
echo "更新依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
echo "重启服务..."
sudo systemctl restart vocabulary

echo "更新完成！"
sudo systemctl status vocabulary
```

使用方法：
```bash
chmod +x update_vocabulary.sh
./update_vocabulary.sh
```

## 中国大陆服务器Git管理方案

### 方案A：混合策略（推荐）

适用于已经使用scp方式部署的服务器，添加本地git管理：

#### 1. 初始化本地git仓库

```bash
# 在服务器上执行
cd /var/www/vocabulary

# 备份当前环境
sudo cp -r . ../vocabulary_backup_$(date +%Y%m%d_%H%M%S)

# 初始化git仓库（仅用于版本管理）
git init
git add .
git commit -m "Initial commit - current production state"

# 设置git配置
git config --global user.name "Server Admin"
git config --global user.email "admin@yourdomain.com"

# 可选：添加gitee远程仓库（备用）
git remote add origin https://gitee.com/your-username/vocabulary-trainer.git
```

#### 2. 继续使用scp更新方式

```bash
# 在本地电脑执行更新
scp -r * root@82.157.204.20:/var/www/vocabulary/

# 在服务器上提交版本
cd /var/www/vocabulary
git add .
git commit -m "Update from local development - $(date)"
```

#### 3. 优势

- **保持现有工作流**：不改变scp的使用习惯
- **版本管理**：本地有完整的版本历史
- **网络友好**：不依赖外部网络连接
- **渐进式迁移**：可以逐步测试git pull方式

### 方案B：完全迁移到Gitee

#### 1. 在本地准备Gitee仓库

```bash
# 在本地电脑执行
# 1. 在gitee.com创建新仓库
# 2. 添加gitee远程仓库
git remote add gitee https://gitee.com/your-username/vocabulary-trainer.git

# 3. 推送代码到gitee
git push gitee main
```

#### 2. 在服务器上重新部署

```bash
# 在服务器上执行
cd /var/www
sudo rm -rf vocabulary
sudo git clone https://gitee.com/your-username/vocabulary-trainer.git vocabulary
cd vocabulary

# 恢复配置
sudo cp ../vocabulary_backup_*/.env .
sudo chown -R www-data:www-data .
```

#### 3. 后续更新流程

```bash
# 在服务器上执行
cd /var/www/vocabulary
git pull origin main
sudo systemctl restart vocabulary
```

### 方案C：纯文件管理（最简单）

如果不想使用git，可以继续使用scp + 备份的方式：

```bash
# 更新脚本：update_via_scp.sh
#!/bin/bash

echo "开始更新..."

# 1. 备份当前版本
cd /var/www/vocabulary
sudo cp -r . ../vocabulary_backup_$(date +%Y%m%d_%H%M%S)

# 2. 等待scp传输完成
echo "请执行scp传输..."
read -p "传输完成后按回车继续..."

# 3. 重启服务
sudo systemctl restart vocabulary

echo "更新完成！"
sudo systemctl status vocabulary
```

## 推荐选择

**建议选择方案A（混合策略）**，因为：

1. **风险最小**：不改变现有工作流程
2. **功能最全**：既有版本管理，又保持简单
3. **适应性强**：可以根据需要逐步迁移
4. **网络友好**：不依赖外部网络连接

如果后续需要团队协作或自动化部署，再考虑迁移到方案B。 

看起来是网络连接问题，GitHub连接不稳定。让我们用更可靠的方法：

## 方法1：等待并重试

```bash
# 等待一下，然后重试
sleep 10
sudo git clone https://github.com/Stoic42/vocabulary-trainer.git .
```

## 方法2：使用SSH方式（如果可用）

```bash
# 尝试SSH方式
sudo git clone git@github.com:Stoic42/vocabulary-trainer.git .
```

## 方法3：手动上传（最可靠）

在**你的本地电脑**上执行：

```bash
# 压缩项目文件
tar -czf vocabulary_project.tar.gz --exclude='.git' --exclude='venv' --exclude='__pycache__' .

# 上传压缩包
scp vocabulary_project.tar.gz root@82.157.204.20:/var/www/
```

然后在**服务器**上执行：

```bash
# 解压文件
cd /var/www/vocabulary_new
sudo tar -xzf ../vocabulary_project.tar.gz

# 复制重要文件
sudo cp ../vocabulary/.env .
sudo cp ../vocabulary/vocabulary.db .

# 替换目录
cd /var/www
sudo mv vocabulary vocabulary_old
sudo mv vocabulary_new vocabulary

# 设置权限
sudo chown -R www-data:www-data vocabulary
sudo chmod -R 755 vocabulary
sudo chmod 644 vocabulary/vocabulary.db

# 重启服务
sudo systemctl restart vocabulary
```

## 方法4：直接从本地上传整个目录

在**你的本地电脑**上执行：

```bash
# 上传整个项目目录
scp -r . root@82.157.204.20:/var/www/vocabulary_new/
```

然后在**服务器**上执行：

```bash
# 复制重要文件
sudo cp /var/www/vocabulary/.env /var/www/vocabulary_new/
sudo cp /var/www/vocabulary/vocabulary.db /var/www/vocabulary_new/

# 替换目录
cd /var/www
sudo mv vocabulary vocabulary_old
sudo mv vocabulary_new vocabulary

# 设置权限和重启
sudo chown -R www-data:www-data vocabulary
sudo chmod -R 755 vocabulary
sudo chmod 644 vocabulary/vocabulary.db
sudo systemctl restart vocabulary
```

建议先试试方法4，这是最直接可靠的！请告诉我你想用哪种方法。

## 部署后检查

完成部署后，请检查以下几点确保部署成功：

1. 访问网站，确认能正常打开
1. 访问网站，如果出现502错误，按以下步骤排查:
   如果返回502错误，可能是以下原因：

   1. Gunicorn服务未正常运行
   ```bash
   # 检查Gunicorn进程
   ps aux | grep gunicorn
   
   # 检查8000端口是否在监听
   sudo netstat -tlnp | grep :8000
   ```

   2. Nginx与Gunicorn通信问题
   ```bash
   # 检查Nginx错误日志
   sudo tail -f /var/log/nginx/error.log
   
   # 如果看到"connect() failed (111: Connection refused)"错误
   # 说明Gunicorn没有正常监听8000端口
   # 如果服务启动失败，按以下步骤排查:

   # 1. 检查日志获取具体错误信息
   sudo journalctl -u vocabulary -n 50
   # 2. 检查gunicorn配置文件是否存在
   ls -l gunicorn.conf.py
   
   # 3. 如果配置文件不存在，创建一个新的
   sudo tee gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
preload_app = True
chdir = "/var/www/vocabulary"
accesslog = "/var/www/vocabulary/logs/gunicorn_access.log"
errorlog = "/var/www/vocabulary/logs/gunicorn_error.log"
wsgi_app = "app:app"
EOF

   # 4. 确保日志目录存在
   sudo mkdir -p /var/www/vocabulary/logs
   sudo chown -R www-data:www-data /var/www/vocabulary/logs
   
   # 5. 重启服务
   sudo systemctl restart vocabulary

   # 2. 检查gunicorn是否正确安装在虚拟环境中
   cd /var/www/vocabulary
   source venv/bin/activate
   which gunicorn
   pip install gunicorn --upgrade

   # 3. 检查app.py是否存在且有正确的app对象
   ls -l app.py
   cat app.py | grep "app = Flask"

   # 4. 检查gunicorn配置文件权限和内容
   sudo chmod 644 gunicorn.conf.py
   cat gunicorn.conf.py

   # 5. 尝试不使用配置文件直接启动，看是否成功
   cd /var/www/vocabulary
   source venv/bin/activate
   gunicorn --bind 127.0.0.1:8000 --workers 3 app:app

   # 6. 如果直接启动成功，说明是配置文件问题，重新生成配置
   sudo tee gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
preload_app = True
chdir = "/var/www/vocabulary"
accesslog = "/var/www/vocabulary/logs/gunicorn_access.log"
errorlog = "/var/www/vocabulary/logs/gunicorn_error.log"
wsgi_app = "app:app"
EOF

   # 7. 确保日志目录存在且有正确权限
   sudo mkdir -p /var/www/vocabulary/logs
   sudo chown -R www-data:www-data /var/www/vocabulary/logs

   # 8. 重启服务测试
   sudo systemctl restart vocabulary
   sudo systemctl status vocabulary
   ```

   3. 文件权限问题
   ```bash
   # 修复文件权限
   sudo chown -R www-data:www-data /var/www/vocabulary
   sudo chmod -R 755 /var/www/vocabulary
   sudo chmod 644 /var/www/vocabulary/vocabulary.db
   ```

   4. 虚拟环境问题
   ```bash
   # 重新激活虚拟环境并测试
   cd /var/www/vocabulary
   source venv/bin/activate
   python app.py
   ```

   5. 配置文件问题
   ```bash
   # 检查gunicorn配置
   cat gunicorn.conf.py
   
   # 确保bind地址正确
   # bind = "127.0.0.1:8000"
   ```

   a. 检查Gunicorn服务状态:
   ```bash
   sudo systemctl status vocabulary
   sudo journalctl -u vocabulary -f
   ```

   b. 检查Nginx配置和状态:
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   sudo tail -f /var/log/nginx/error.log
   ```
   b.1. 如果出现"Failed to locate executable /var/www/vocabulary/venv/bin/gunicorn"错误:
   ```bash
   # 重新创建并激活虚拟环境
   cd /var/www/vocabulary
   python3 -m venv venv
   source venv/bin/activate

   # 重新安装gunicorn和其他依赖
   pip install gunicorn
   pip install -r requirements.txt

   # 确认gunicorn已安装并可执行
   which gunicorn
   ls -l /var/www/vocabulary/venv/bin/gunicorn

   # 重启服务
   sudo systemctl restart vocabulary
   ```

   b.2. 如果问题仍然存在，检查systemd服务文件:
   ```bash
   # 编辑服务文件
   sudo nano /etc/systemd/system/vocabulary.service

   # 确保ExecStart路径正确:
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/vocabulary
   Environment="PATH=/var/www/vocabulary/venv/bin"
   ExecStart=/var/www/vocabulary/venv/bin/gunicorn --config /var/www/vocabulary/gunicorn.conf.py

   # 重新加载systemd并重启服务
   sudo systemctl daemon-reload
   sudo systemctl restart vocabulary
   ```

   c. 检查端口监听:
   ```bash
   sudo netstat -tlnp | grep :8000  # 检查Gunicorn端口
   sudo netstat -tlnp | grep :80    # 检查Nginx端口
   ```

   d. 检查文件权限:
   ```bash
   sudo chown -R www-data:www-data /var/www/vocabulary
   sudo chmod -R 755 /var/www/vocabulary
   sudo chmod 644 /var/www/vocabulary/vocabulary.db
   ```

   e. 手动测试Gunicorn:
   ```bash
   cd /var/www/vocabulary
   source venv/bin/activate
   gunicorn --config gunicorn.conf.py app:app
   ```

   f. 重启服务:
   ```bash
   sudo systemctl restart vocabulary
   sudo systemctl restart nginx
   ```


2. 尝试登录账号，确认能正常登录
3. 检查数据是否完整，比如词库内容
4. 查看服务器日志是否有错误:
   ```bash
   sudo journalctl -u vocabulary -n 50
   ```

如果发现问题：
- 检查 `.env` 文件配置是否正确
- 确认数据库文件权限设置正确
- 查看 nginx 错误日志: `/var/log/nginx/error.log`
- 如有必要可以回滚:
  ```bash
  cd /var/www
  sudo mv vocabulary vocabulary_broken
  sudo mv vocabulary_old vocabulary
  sudo systemctl restart vocabulary
  ```
