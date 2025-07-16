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