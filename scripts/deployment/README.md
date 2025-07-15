# 部署脚本目录

本目录包含词汇训练营应用部署相关的脚本和配置文件。

## 脚本说明

### env_prod_template.txt
- **用途**: 生产环境配置文件模板
- **使用**: 复制为 `.env` 并填写实际配置
- **包含**: 数据库路径、日志配置、密钥等

### final_check.py
- **用途**: 部署后完整性检查脚本
- **功能**: 
  - 检查数据库连接
  - 验证文件权限
  - 测试服务状态
  - 检查日志文件

### final_check_simple.py
- **用途**: 简化版部署检查脚本
- **功能**: 基础的服务状态检查
- **适用**: 快速验证部署是否成功

## 使用流程

1. **部署前**: 使用 `env_prod_template.txt` 创建配置文件
2. **部署后**: 运行 `final_check.py` 或 `final_check_simple.py` 验证部署
3. **维护时**: 定期运行检查脚本确保服务正常

## 运行方式

### 方法1：从项目根目录运行（推荐）
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行完整检查
python scripts/deployment/final_check.py

# 运行简化检查
python scripts/deployment/final_check_simple.py
```

### 方法2：从脚本目录运行
```bash
# 进入脚本目录
cd scripts/deployment

# 激活虚拟环境（需要回到项目根目录）
source ../../venv/bin/activate

# 运行脚本
python final_check.py
python final_check_simple.py
```

## 路径说明

所有脚本已更新为使用绝对路径，可以从任何位置运行：
- 数据库文件路径：自动定位到项目根目录的 `vocabulary.db`
- 输出文件路径：自动保存到项目根目录
- 配置文件路径：相对于项目根目录

## 注意事项

- 确保在运行脚本前已激活虚拟环境
- 脚本会自动查找项目根目录的数据库文件
- 如果遇到路径问题，请从项目根目录运行脚本 