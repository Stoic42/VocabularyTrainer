# 词汇训练营 (Vocabulary Trainer)

一个基于Flask的英语词汇学习应用，支持SRS间隔重复算法和个性化学习路径。

## 项目结构

```
VocabularyTrainer/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
├── vocabulary.db         # 主数据库文件
├── 
├── docs/                 # 文档目录
│   ├── deployment/       # 部署相关文档
│   │   ├── DEPLOYMENT.md      # 基础部署指南
│   │   ├── DEPLOYMENTV2.md    # 增强版部署手册
│   │   ├── DEPLOYMENTV3.md    # 生产环境更新指南
│   │   └── README.md          # 部署文档说明
│   └── ...              # 其他文档
├── 
├── scripts/              # 脚本目录
│   ├── deployment/       # 部署相关脚本
│   │   ├── env_prod_template.txt  # 生产环境配置模板
│   │   ├── final_check.py         # 部署检查脚本
│   │   ├── final_check_simple.py  # 简化检查脚本
│   │   └── README.md              # 部署脚本说明
│   ├── database/         # 数据库管理脚本
│   │   ├── check_server_db.py     # 服务器数据库检查
│   │   ├── compare_databases.py   # 数据库比较
│   │   ├── sync_new_users.py      # 用户数据同步
│   │   └── README.md              # 数据库脚本说明
│   ├── debug/            # 调试脚本
│   ├── fixes/            # 修复脚本
│   ├── maintenance/      # 维护脚本
│   ├── sync/             # 同步脚本
│   └── audio/            # 音频处理脚本
├── 
├── templates/            # HTML模板
├── assets/               # 静态资源 (字体、图片等)
├── wordlists/            # 词汇列表
├── logs/                 # 日志文件
└── backups/              # 备份文件
```

## 快速开始

### 本地开发
```bash
# 克隆项目
git clone https://github.com/Stoic42/vocabulary-trainer.git
cd vocabulary-trainer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 生产环境部署

请参考 `docs/deployment/` 目录中的部署文档：

- **首次部署**: 使用 `DEPLOYMENTV2.md`
- **环境更新**: 使用 `DEPLOYMENTV3.md`
- **学习参考**: 查看 `DEPLOYMENT.md`

## 主要功能

- 📚 多级别词汇学习（初中、高中、CET4等）
- 🔄 SRS间隔重复算法
- 🎯 个性化学习路径
- 📊 学习进度统计
- 🎵 音频发音支持
- 📱 响应式设计

## 技术栈

- **后端**: Flask, SQLite
- **前端**: HTML, CSS, JavaScript
- **部署**: Nginx, Gunicorn
- **音频**: gTTS (Google Text-to-Speech)

## 维护工具

项目提供了丰富的维护脚本，位于 `scripts/` 目录：

- **部署检查**: `scripts/deployment/final_check.py`
- **数据库管理**: `scripts/database/`
- **调试工具**: `scripts/debug/`
- **修复脚本**: `scripts/fixes/`

## 开发文档

详细的开发文档位于 `docs/` 目录：

- **部署指南**: `docs/deployment/`
- **静态资源开发**: `docs/ASSETS_DEVELOPMENT.md`
- **文件组织说明**: `docs/FILE_ORGANIZATION.md`

## 项目规范化

本项目正在进行全面的标准化改进，详细信息请参考：

- 📋 **[标准化指南](docs/STANDARDIZATION_GUIDE.md)** - 项目标准化总体指南
- 📁 **[规范化需求](.kiro/specs/)** - 详细的规范化需求文档
- 🎯 **[实施优先级](.kiro/specs/README.md)** - 规范化项目优先级和实施指南

### 当前规范化项目

1. 🔧 **API接口标准化** - 建立RESTful API标准
2. 🗄️ **数据库架构优化** - 规范化数据模型
3. 🏗️ **Blueprint架构迁移** - 实现模块化架构
4. 🤖 **AI多模态记忆系统** - 标准化AI功能
5. 🔗 **个性化数据打通** - 整合多源数据
6. 🚀 **部署流程标准化** - 自动化部署
7. 📝 **代码质量标准** - 建立代码规范

## 贡献

欢迎提交Issue和Pull Request！

在贡献代码前，请：
1. 阅读 [标准化指南](docs/STANDARDIZATION_GUIDE.md)
2. 遵循项目的代码规范
3. 确保测试通过
4. 更新相关文档

## 许可证

MIT License 