# 项目目录结构说明

## 主要目录

### `/docs/` - 文档目录
存放所有项目相关的文档、README文件和报告：
- `README*.md` - 各种功能说明文档
- `BUGFIX*.md` - 错误修复说明
- `data_quality_report.md` - 数据质量报告
- `音频问题解决方案.md` - 音频相关问题解决方案
- `*.txt` - 各种文本报告和日志

### `/scripts/` - 脚本目录
按功能分类的各种脚本文件：

#### `/scripts/fixes/` - 修复脚本
存放各种一次性修复脚本：
- `fix_*.py` - 各种数据修复脚本
- `fix_*.js` - 前端修复脚本
- `inject_*.py` - 脚本注入工具
- `fix_*.html` - 修复相关的HTML文件

#### `/scripts/debug/` - 调试和检查脚本
存放调试、检查和测试脚本：
- `debug_*.py` - 调试脚本
- `check_*.py` - 数据检查脚本
- `analyze_*.py` - 数据分析脚本
- `test_*.py` - 测试脚本
- `show_exact_duplicates.py` - 重复数据检查
- `find_similar_words.py` - 相似词查找

#### `/scripts/sync/` - 同步脚本
存放数据同步相关脚本：
- `sync_*.py` - 各种同步脚本
- `cleanup_and_sync_*.py` - 清理和同步脚本

#### `/scripts/data_import/` - 数据导入脚本
存放数据导入和处理脚本：
- `import_*.py` - 数据导入脚本
- `extract_*.py` - 数据提取脚本
- `add_*.py` - 数据添加脚本
- `conver_*.py` - 数据转换脚本

#### `/scripts/maintenance/` - 维护脚本
存放系统维护相关脚本：
- `cleanup_*.py` - 清理脚本
- `initialize_app.py` - 应用初始化
- `manage_users.py` - 用户管理
- `create_error_logs_table.py` - 错误日志表创建
- `reimport_*.py` - 重新导入脚本
- `*.bat` - 批处理文件

#### `/scripts/audio/` - 音频处理脚本
存放音频相关的处理脚本：
- 音频映射脚本
- 音频路径修复脚本
- 音频验证脚本

### `/backups/` - 备份目录
存放各种备份文件：
- `app.py.bak.*` - 应用文件备份

### `/test/` - 测试目录
存放测试相关文件：
- `test_*.html` - 测试页面
- `test_*.py` - 测试脚本

## 核心应用文件

### 主应用文件
- `app.py` - 主应用程序
- `config.py` - 配置文件
- `admin_routes.py` - 管理员路由
- `requirements.txt` - Python依赖

### 其他重要文件
- `DEVELOPMENT_GUIDE.md` - 开发指南
- `export_none_meaning_words.py` - 导出无意义词汇
- `final_check*.py` - 最终检查脚本

## 整理说明

本次整理将原本散落在主目录下的各种脚本和文档文件按功能进行了分类整理：

1. **文档集中化** - 所有README和文档文件统一放在`docs/`目录
2. **脚本分类** - 按功能将脚本分为修复、调试、同步、导入、维护、音频等类别
3. **备份管理** - 备份文件统一放在`backups/`目录
4. **测试分离** - 测试文件统一放在`test/`目录

这样的整理提高了项目的可维护性，使文件结构更加清晰，便于后续开发和维护。 