# 闪退问题修复报告

## 问题描述

客户反馈（2025年7月15日）：
- 软件在使用过程中出现闪退两次
- 页面恢复到首页，已输入部分变空
- 需要重新开始测试

## 问题分析

### 1. 根本原因：TTS音频生成超时导致Worker崩溃

通过分析服务器日志，发现问题的根本原因是：

```
[2025-07-15 21:12:27 +0800] [305483] [CRITICAL] WORKER TIMEOUT (pid:305486)
[2025-07-15 21:25:20 +0800] [305483] [CRITICAL] WORKER TIMEOUT (pid:305485)
```

**具体问题：**
- TTS音频生成请求（`/api/tts/`）在连接Google TTS服务时超时
- 导致gunicorn Worker进程被强制终止
- 用户正在进行的测试被中断，页面自动刷新或跳转到首页

### 2. 页面状态管理问题

**现状：**
- 所有功能都在同一个页面实现
- 页面刷新会导致状态丢失
- 用户需要重新选择功能和列表

## 解决方案

### 1. TTS超时保护机制

**修改文件：** `app.py`

**改进内容：**
- 添加30秒超时控制，防止Worker崩溃
- 使用signal模块实现超时处理
- 优雅处理超时错误，返回408状态码
- 增强错误日志记录

```python
# 添加超时控制，防止Worker崩溃
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("TTS生成超时")

# 设置30秒超时
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

try:
    tts = gTTS(text=processed_word, lang='en', slow=False)
    tts.save(filepath)
except TimeoutError:
    app.logger.error(f"TTS生成超时: {word}")
    return {'error': 'TTS生成超时，请稍后重试'}, 408
finally:
    signal.alarm(0)  # 取消超时
```

### 2. Gunicorn配置优化

**修改文件：** `gunicorn.conf.py`

**改进内容：**
- 增加Worker超时时间到60秒
- 添加请求数限制和随机抖动
- 优化Keep-alive连接设置

```python
# 增加超时配置
timeout = 60  # Worker超时时间（秒）
keepalive = 2  # Keep-alive连接时间
max_requests = 1000  # Worker处理请求数限制
max_requests_jitter = 100  # 随机抖动，避免所有Worker同时重启
```

### 3. 页面状态管理改进

**修改文件：** `templates/index.html`

**改进内容：**
- 添加完整的页面状态管理
- 实现状态持久化保存和恢复
- 支持测试进度恢复
- 24小时自动清理过期状态

**新增功能：**
- `savePageState()`: 保存页面状态到localStorage
- `restorePageState()`: 恢复页面状态
- `restoreQuizProgress()`: 恢复测试进度
- 自动状态保存触发点

**状态恢复流程：**
1. 页面加载时自动检查是否有未完成的测试
2. 如果有，显示恢复提示对话框
3. 用户确认后恢复测试进度和界面状态
4. 24小时后自动清理过期状态

## 测试验证

### 1. TTS超时保护测试

创建了测试脚本 `test_tts_timeout.py`：
- 测试正常TTS请求
- 测试并发TTS请求
- 验证服务器稳定性

### 2. 状态恢复测试

**测试场景：**
- 页面刷新后状态恢复
- 浏览器关闭重开后状态恢复
- 测试中断后进度恢复

## 部署状态

✅ **已部署完成**
- 服务已重启，新配置生效
- Worker进程正常运行
- 超时保护机制已激活

## 预期效果

### 1. 解决闪退问题
- TTS超时不再导致Worker崩溃
- 用户测试不会被意外中断
- 服务器稳定性显著提升

### 2. 改善用户体验
- 页面刷新后自动恢复状态
- 测试中断后可继续完成
- 减少重复操作

### 3. 系统稳定性
- Worker进程更稳定
- 自动处理超时情况
- 更好的错误处理机制

## 监控建议

### 1. 日志监控
- 关注TTS超时日志
- 监控Worker重启频率
- 跟踪用户状态恢复成功率

### 2. 性能监控
- TTS响应时间
- Worker内存使用
- 并发请求处理能力

## 后续优化

### 1. 短期优化
- 优化TTS缓存策略
- 增加音频文件预生成
- 改进错误提示信息

### 2. 长期规划
- 考虑使用本地TTS服务
- 实现多页面架构
- 添加用户会话管理

## 总结

通过以上修复，成功解决了客户反馈的闪退问题：

1. **根本原因已解决**：TTS超时保护机制防止Worker崩溃
2. **用户体验改善**：页面状态管理确保数据不丢失
3. **系统稳定性提升**：gunicorn配置优化提高服务可靠性

修复后的系统能够：
- 优雅处理TTS超时情况
- 自动恢复用户测试进度
- 提供更好的错误反馈
- 显著减少闪退现象

建议客户继续使用，如有问题及时反馈。 