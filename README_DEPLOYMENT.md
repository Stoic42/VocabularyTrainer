# Lumi单词训练营 - 部署指南

## 数据库初始化说明

在首次部署时，需要特别注意数据库的初始化过程。本应用使用SQLite数据库（vocabulary.db文件），该文件在首次运行`import_data.py`脚本时会自动创建。

### 关于vocabulary.db

- `vocabulary.db`文件不包含在Git仓库中，需要在首次部署时通过运行`import_data.py`脚本创建
- 该数据库包含所有用户信息、单词数据和错误记录
- 默认会创建一个管理员账户：用户名`admin`，密码`admin123`

### 首次部署时的数据导入

在运行`import_data.py`脚本前，请确保以下文件存在：

1. `wordlists/junior_high/junior_high_vocab_random.csv` - 主要单词数据源
2. `wordlists/junior_high/初中 乱序 绿宝书.txt` - 音频路径数据源

如果这些文件不存在，请联系开发人员获取。

## 完整部署流程

1. 克隆仓库：`git clone https://github.com/Stoic42/VocabularyTrainer.git`
2. 安装依赖：`pip install -r requirements.txt`
3. 确保数据源文件存在
4. 初始化数据库：`python import_data.py`
5. 启动应用：`flask run --host=0.0.0.0`

## 常见问题

### 登录失败

如果登录时显示"用户名或密码错误"，可能是因为：

1. 数据库文件（vocabulary.db）不存在 - 请运行`python import_data.py`创建数据库
2. 用户不存在 - 首次运行后会自动创建管理员账户（admin/admin123）

### 数据文件缺失

如果运行`import_data.py`时报错找不到数据文件，请检查：

1. `wordlists/junior_high/junior_high_vocab_random.csv`文件是否存在
2. `wordlists/junior_high/初中 乱序 绿宝书.txt`文件是否存在

如果这些文件不存在，请联系开发人员获取。

## 备份建议

定期备份`vocabulary.db`文件，这是应用的核心数据存储。在进行任何更新或维护前，建议先备份此文件。