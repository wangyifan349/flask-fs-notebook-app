# 📝 flask-fs-notebook-app

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)  
[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)  
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)  

> **flask-fs-notebook-app** 是一个基于 **Flask** 的文件系统 Markdown 笔记本应用。  
> - 每篇笔记存储为 `notes/<标题>.md`  
> - 原生支持 KaTeX 数学公式、Highlight.js 代码高亮  
> - AJAX + Bootstrap Modal 实现新建/重命名/删除  
> - LCS（最长公共子序列）智能排序全文搜索  
> - 附件上传：图片/音频/视频，浏览器内预览/播放  
> - 零数据库依赖，直接在虚拟环境中一键启动  

---

## 📁 仓库结构

```
flask-fs-notebook-app/
├── LICENSE                 # GNU GPL v3 License 全文
├── README.md               # 项目说明（本文件）
├── app.py                  # Flask 应用主入口
├── notes/                  # 存放 .md 笔记（首次运行自动创建）
├── uploads/                # 存放用户上传文件（首次运行自动创建）
└── templates/              # Jinja2 模板目录
    ├── base.html           # 基础布局
    ├── management.html     # 管理页（列表/搜索/增删改/文件上传）
    ├── edit.html           # 编辑页（Markdown 原文编辑）
    └── view.html           # 查看页（渲染/原文切换 + KaTeX + 代码高亮）
```

---

## 🚀 快速开始

1. 克隆或下载本仓库：
   ```bash
   git clone https://github.com/wangyifan349/flask-fs-notebook-app.git
   cd flask-fs-notebook-app
   ```

2. （可选）创建并激活 Python 虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate     # Linux / macOS
   venv\Scripts\activate.bat    # Windows
   ```

3. 安装依赖：
   ```bash
   pip install flask
   ```

4. 运行应用：
   ```bash
   python app.py
   ```

5. 浏览器中访问：
   ```
   http://127.0.0.1:5000/management
   ```

🎉 **现在可以开始创建、编辑、搜索你的 Markdown 笔记，或上传并播放音视频文件了！**

---

## ⚙️ 配置项

在 `app.py` 顶部，你可根据需要修改以下配置：

```python
# Flask Session/Flash 加密密钥，务必换成你自己的随机字符串
app.secret_key = '请替换为你自己的随机字符串'

# 笔记目录与上传目录
NOTE_DIR   = 'notes'
UPLOAD_DIR = 'uploads'

# 允许上传的文件扩展名
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'ogg'}
```

- `NOTE_DIR`、`UPLOAD_DIR`：相对或绝对路径均可  
- `ALLOWED_EXT`：防止任意文件写入，按需增删后缀  

---

## 🔧 主要功能

1. **管理笔记**  
   - 列出 `notes/` 下所有 `.md` 文件（按最新修改时间倒序）  
   - AJAX 新建 / 重命名 / 删除 笔记（Bootstrap Modal）  
   - 全文搜索：子串匹配 + LCS 排序  

2. **编辑笔记**  
   - Markdown 原文编辑  
   - 保存后自动刷新到查看页  

3. **查看笔记**  
   - 渲染模式：Markdown-It + KaTeX + Highlight.js  
   - 原文模式：展示纯文本 `.md` 内容  
   - 页面按钮切换两种模式  

4. **文件上传与管理**  
   - 在管理页底部上传图片、音频、视频  
   - 列表展示所有上传文件  
   - 图片直接预览，音视频嵌入播放  

---

## 💻 文件说明

### `app.py`

- 路由定义：`/management`、`/note/<action>`、`/edit/<title>`、`/view/<title>`、`/search`、`/upload`、`/files`、`/uploads/<filename>`  
- 工具函数：`note_path`（安全文件名）、`list_notes`（读取并排序）、`lcs`（最长公共子序列）  

### `templates/`

- `base.html`：页面基础布局、Bootstrap 引入  
- `management.html`：笔记列表、搜索框、文件上传、Modal 控件与 JS  
- `edit.html`：Markdown 原文编辑表单  
- `view.html`：Markdown 渲染、KaTeX、Highlight.js、原文/渲染切换  

---

## 📋 使用示例

- **新建笔记**：点击「新建笔记」，输入标题，点击「确定」  
- **重命名**：在某行点击「重命名」，输入新标题，确定  
- **删除**：在某行点击「删除」，确认对话框  
- **搜索**：输入关键词，点击「🔍」，列表按相关度展示  
- **编辑**：点击「查看」→「编辑」→修改 →「保存」  
- **查看**：渲染模式支持公式与代码高亮；切到「原文」看 Markdown 源  
- **上传文件**：管理页底部选择文件→上传；列表中点击即可预览/播放  

---

## 📦 无数据库依赖

本项目完全基于文件系统存储笔记和附件，无需安装 SQLite、PostgreSQL 等数据库。适合轻量级个人笔记或小团队内部分享使用。

---

## 📜 许可证

本项目遵循 **GNU General Public License v3.0** (GPL-3.0) 许可协议。  
详细许可条款请见 [LICENSE](LICENSE) 文件。

---

Made with ♥ by **王一帆**  
欢迎 ⭐️ Star 和 💬 Issue / PR！
