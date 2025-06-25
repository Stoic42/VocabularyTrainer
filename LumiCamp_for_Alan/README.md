# Lumi单词训练营

## 部署说明

### 第一步：安装Miniconda

1. 双击Miniconda安装包，按照默认设置完成安装。

### 第二步：创建环境

1. 打开Anaconda Prompt（通过开始菜单找到）
2. 使用cd命令进入LumiCamp文件夹：
   ```
   D:
   cd D:\LumiCamp_for_Alan
   ```
3. 使用environment.yml文件创建本地Conda环境：
   ```
   conda env create -f environment.yml --prefix ./env
   ```
   这一步会在当前文件夹下创建一个名为env的子文件夹，并将整个Python环境安装在里面。

### 第三步：导入词汇数据

1. 环境创建成功后，激活这个本地环境：
   ```
   conda activate ./env
   ```
2. 运行数据导入脚本，将初中和高中词汇导入数据库：
   ```
   python import_data.py
   python import_senior_high_data.py
   ```

### 第四步：启动应用

1. 双击`start_lumi.bat`文件启动应用。
2. 在浏览器中访问 http://127.0.0.1:5000 即可使用Lumi单词训练营。

## 使用说明

1. 注册账号：首次使用需要注册账号。
2. 登录：使用注册的账号登录。
3. 选择词书和单元：在主界面选择要学习的词书和单元。
4. 开始学习：点击开始按钮，进入学习模式。
5. 查看错题：在历史记录中可以查看错题。

## 文件夹结构

- `app.py`：应用入口点
- `import_data.py`：初中词汇导入脚本
- `import_senior_high_data.py`：高中词汇导入脚本
- `templates/`：HTML模板文件
- `assets/`：静态资源文件（CSS、JS、图片等）
- `wordlists/`：词汇数据文件
- `env/`：Python环境（由conda创建）
- `vocabulary.db`：SQLite数据库文件（由导入脚本创建）