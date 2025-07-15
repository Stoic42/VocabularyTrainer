# 文件整理说明

## 整理概述

本次整理将项目根目录中的部署文档和脚本文件进行了分类整理，提高了项目的可维护性和可读性。

## 整理内容

### 1. 部署文档整理

**原位置**: 项目根目录
**新位置**: `docs/deployment/`

| 原文件名 | 新位置 | 说明 |
|---------|--------|------|
| `DEPLOYMENT.md` | `docs/deployment/DEPLOYMENT.md` | 基础部署指南 |
| `DEPLOYMENTV2.md` | `docs/deployment/DEPLOYMENTV2.md` | 增强版部署手册 |
| `DEPLOYMENTV3.md` | `docs/deployment/DEPLOYMENTV3.md` | 生产环境更新指南 |

### 2. 部署脚本整理

**原位置**: 项目根目录
**新位置**: `scripts/deployment/`

| 原文件名 | 新位置 | 说明 |
|---------|--------|------|
| `env_prod_template.txt` | `scripts/deployment/env_prod_template.txt` | 生产环境配置模板 |
| `final_check.py` | `scripts/deployment/final_check.py` | 部署检查脚本 |
| `final_check_simple.py` | `scripts/deployment/final_check_simple.py` | 简化检查脚本 |

### 3. 数据库脚本整理

**原位置**: 项目根目录
**新位置**: `scripts/database/`

| 原文件名 | 新位置 | 说明 |
|---------|--------|------|
| `check_server_db.py` | `scripts/database/check_server_db.py` | 服务器数据库检查 |
| `compare_databases.py` | `scripts/database/compare_databases.py` | 数据库比较脚本 |
| `sync_new_users.py` | `scripts/database/sync_new_users.py` | 用户数据同步 |

### 4. 调试脚本整理

**原位置**: 项目根目录
**新位置**: `scripts/debug/`

| 原文件名 | 新位置 | 说明 |
|---------|--------|------|
| `export_none_meaning_words.py` | `scripts/debug/export_none_meaning_words.py` | 导出无意义词汇 |

### 5. 静态资源文档整理

**原位置**: `assets/README.md`
**新位置**: `docs/ASSETS_DEVELOPMENT.md`

| 原文件名 | 新位置 | 说明 |
|---------|--------|------|
| `assets/README.md` | `docs/ASSETS_DEVELOPMENT.md` | 静态资源开发指南 |

## 新增文档

### 1. 主README.md
- **位置**: 项目根目录
- **内容**: 项目概述、快速开始、功能说明、技术栈等

### 2. 部署文档README.md
- **位置**: `docs/deployment/README.md`
- **内容**: 部署文档版本说明和使用建议

### 3. 部署脚本README.md
- **位置**: `scripts/deployment/README.md`
- **内容**: 部署脚本功能说明和使用方法

### 4. 数据库脚本README.md
- **位置**: `scripts/database/README.md`
- **内容**: 数据库脚本功能说明和使用流程

### 5. 静态资源开发指南
- **位置**: `docs/ASSETS_DEVELOPMENT.md`
- **内容**: 静态资源管理规范和开发流程

## 目录结构优化

### 整理前
```
VocabularyTrainer/
├── DEPLOYMENT.md
├── DEPLOYMENTV2.md
├── DEPLOYMENTV3.md
├── env_prod_template.txt
├── final_check.py
├── final_check_simple.py
├── check_server_db.py
├── compare_databases.py
├── sync_new_users.py
├── export_none_meaning_words.py
├── assets/README.md
└── ... (其他文件)
```

### 整理后
```
VocabularyTrainer/
├── README.md                    # 新增：项目主文档
├── docs/
│   └── deployment/
│       ├── README.md            # 新增：部署文档说明
│       ├── DEPLOYMENT.md
│       ├── DEPLOYMENTV2.md
│       └── DEPLOYMENTV3.md
├── scripts/
│   ├── deployment/
│   │   ├── README.md            # 新增：部署脚本说明
│   │   ├── env_prod_template.txt
│   │   ├── final_check.py
│   │   └── final_check_simple.py
│   ├── database/
│   │   ├── README.md            # 新增：数据库脚本说明
│   │   ├── check_server_db.py
│   │   ├── compare_databases.py
│   │   └── sync_new_users.py
│   └── debug/
│       └── export_none_meaning_words.py
├── docs/
│   ├── deployment/       # 部署文档
│   ├── ASSETS_DEVELOPMENT.md  # 静态资源开发指南
│   └── FILE_ORGANIZATION.md   # 文件整理说明
└── ... (其他文件)
```

## 使用建议

### 1. 部署相关
- **首次部署**: 查看 `docs/deployment/DEPLOYMENTV2.md`
- **环境更新**: 查看 `docs/deployment/DEPLOYMENTV3.md`
- **配置模板**: 使用 `scripts/deployment/env_prod_template.txt`

### 2. 数据库管理
- **检查服务器**: 运行 `scripts/database/check_server_db.py`
- **比较数据库**: 运行 `scripts/database/compare_databases.py`
- **同步数据**: 运行 `scripts/database/sync_new_users.py`

### 3. 部署验证
- **完整检查**: 运行 `scripts/deployment/final_check.py`
- **快速检查**: 运行 `scripts/deployment/final_check_simple.py`

### 4. 静态资源开发
- **开发指南**: 查看 `docs/ASSETS_DEVELOPMENT.md`
- **同步定制版本**: 使用 `scripts/sync/sync_to_custom.py`

## 维护说明

1. **新增部署文档**: 放在 `docs/deployment/` 目录
2. **新增部署脚本**: 放在 `scripts/deployment/` 目录
3. **新增数据库脚本**: 放在 `scripts/database/` 目录
4. **新增调试脚本**: 放在 `scripts/debug/` 目录
5. **新增开发文档**: 放在 `docs/` 目录
6. **更新README**: 及时更新对应目录的README.md文件

## 注意事项

- 所有脚本的路径引用可能需要更新
- 部署文档中的路径说明需要相应调整
- 建议在运行脚本前先检查路径是否正确 