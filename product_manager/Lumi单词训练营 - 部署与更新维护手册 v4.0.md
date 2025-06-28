# **Lumi单词训练营 \- 部署与更新维护手册**

版本： 4.0 (Git工作流 / 仅C盘环境 / 最终版)  
更新日期： 2025年6月27日  
目的： 本文档为技术维护人员提供在学校服务器（仅C盘）上，使用Git工作流进行“Lumi单词训练营”应用的首次部署及后续版本更新的标准化操作流程（SOP）。

## **一、 首次部署操作规程 (SOP)**

*此流程仅需在全新的电脑上执行一次。*

### **准备阶段：环境安装**

1. **安装Git**: 访问 [git-scm.com](https://git-scm.com/downloads) 下载并安装Git，安装过程中可全部使用默认选项。  
2. **安装Anaconda**: 访问 [anaconda.com/download](https://www.anaconda.com/download) 下载并安装Anaconda（Python 3.x 版本）。**强烈推荐**在安装时勾选“Add Anaconda3 to my PATH”选项。

### **部署阶段：项目配置与启动**

*请严格按照以下顺序，在 **Anaconda Prompt** 中执行所有命令。*

1. **启动Anaconda Prompt**:  
   * 从Windows“开始”菜单中，找到并打开 **Anaconda Prompt**。  
2. **创建独立运行环境**:  
   * 我们将在C盘的用户目录下创建一个文件夹来存放所有conda环境，以保持系统整洁。

conda create \--prefix C:\\Users\\%USERNAME%\\conda\_envs\\VocabMVP python=3.11 \-y

3. **激活环境**:  
   conda activate C:\\Users\\%USERNAME%\\conda\_envs\\VocabMVP

   * 成功后，命令行最左侧会显示环境路径。  
4. **进入工作目录**:  
   * 我们将项目存放在“文档”文件夹中，便于管理。

cd Documents

5. **从GitHub克隆项目代码**:  
   * 此命令会将最新的应用程序代码从云端下载到本地。

git clone https://github.com/Stoic42/VocabularyTrainer.git

6. **进入项目文件夹**:  
   cd VocabularyTrainer

7. **安装所有必需的依赖库**:  
   * 此命令会自动读取项目中的requirements.txt文件，并安装所有必需的Python库（如Flask）。

pip install \-r requirements.txt

8. **初始化数据库与数据**:  
   * 运行数据转换/导入脚本，创建并填充数据库。

   python import\_data.py

   * *(注意：请根据您最终的脚本名称进行调整)*  
9. **启动应用服务**:  
   flask run \--host=0.0.0.0

   * 当看到 \* Running on http://... 的提示时，代表服务器已成功启动。校内其他电脑可以通过访问该电脑的IP地址来使用本应用。

## **二、 日常更新操作规程 (SOP)**

*当开发者在GitHub上发布新版本后，请按此流程进行更新。*

1. **启动Anaconda Prompt**。  
2. **进入项目文件夹**:  
   cd C:\\Users\\%USERNAME%\\Documents\\VocabularyTrainer

3. **激活项目环境**:  
   conda activate C:\\Users\\%USERNAME%\\conda\_envs\\VocabMVP

4. **(核心) 拉取最新代码**:  
   * 此命令会从GitHub下载最新的程序文件。

git pull origin main

5. **(重要) 更新依赖库**:  
   * 这一步确保新版本中增加的任何新库都能被及时安装。

pip install \-r requirements.txt

6. **重启服务**:  
   * 如果服务器正在运行，请在对应的Anaconda Prompt窗口中按 Ctrl \+ C 停止它。  
   * 然后重新运行启动命令：

flask run \--host=0.0.0.0

**更新完成！** 这套基于Git的专业工作流，是目前最高效、最灵活、也最适合您当前情况的维护方案。