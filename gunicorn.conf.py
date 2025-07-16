bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
preload_app = True
chdir = "/var/www/vocabulary"
accesslog = "/var/www/vocabulary/logs/gunicorn_access.log"
errorlog = "/var/www/vocabulary/logs/gunicorn_error.log"
wsgi_app = "app:app"

# 增加超时配置
timeout = 60  # Worker超时时间（秒）
keepalive = 2  # Keep-alive连接时间
max_requests = 1000  # Worker处理请求数限制
max_requests_jitter = 100  # 随机抖动，避免所有Worker同时重启
