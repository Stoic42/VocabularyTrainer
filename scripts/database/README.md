# 数据库脚本目录

本目录包含词汇训练营应用数据库相关的管理脚本。

## 脚本说明

### check_server_db.py
- **用途**: 检查服务器数据库状态
- **功能**: 
  - 连接服务器数据库
  - 检查表结构
  - 验证数据完整性
  - 生成检查报告

### compare_databases.py
- **用途**: 比较本地和服务器数据库
- **功能**:
  - 对比表结构差异
  - 统计数据量差异
  - 识别新增/修改的记录
  - 生成详细对比报告

### sync_new_users.py
- **用途**: 同步新用户数据
- **功能**:
  - 从服务器数据库提取新用户
  - 同步用户错误日志
  - 保持数据一致性
  - 避免数据冲突

## 使用场景

### 数据同步流程
1. **检查服务器状态**: `check_server_db.py`
2. **比较数据差异**: `compare_databases.py`
3. **同步新数据**: `sync_new_users.py`

### 部署后验证
- 运行 `check_server_db.py` 验证数据库连接
- 使用 `compare_databases.py` 确保数据完整性

## 运行方式

### 方法1：从项目根目录运行（推荐）
```bash
# 激活虚拟环境
source venv/bin/activate

# 检查服务器数据库
python scripts/database/check_server_db.py

# 比较数据库
python scripts/database/compare_databases.py

# 同步新用户
python scripts/database/sync_new_users.py
```

### 方法2：从脚本目录运行
```bash
# 进入脚本目录
cd scripts/database

# 激活虚拟环境（需要回到项目根目录）
source ../../venv/bin/activate

# 运行脚本
python check_server_db.py
python compare_databases.py
python sync_new_users.py
```

## 路径说明

所有脚本已更新为使用绝对路径：
- **本地数据库**: 自动定位到项目根目录的 `vocabulary.db`
- **服务器数据库**: 自动定位到项目根目录的 `vocabulary_server.db`
- **输出文件**: 自动保存到项目根目录

## 注意事项

- 运行前确保数据库文件路径正确
- 同步脚本会修改数据库，请先备份
- 建议在测试环境验证后再在生产环境使用
- 脚本可以从任何位置运行，会自动查找项目根目录的数据库文件 