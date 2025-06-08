# 📝 Flask FS Notebook App

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)  
[![Python 3](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)  
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)  

> 一个基于 Flask 的文件系统 Markdown 笔记本，支持 KaTeX、代码高亮、LCS 搜索、文件上传与音视频播放，零依赖数据库，轻量易用！

---

## 🗂 目录结构

```
flask-fs-notebook-app/
├── LICENSE                 # GPL-3.0 License
├── README.md               # 项目说明
├── app.py                  # Flask 应用主入口
├── notes/                  # 存放 .md 笔记（首次运行自动创建）
├── uploads/                # 存放用户上传文件（首次运行自动创建）
└── templates/              # Jinja2 模板目录
    ├── base.html           # 基础布局
    ├── management.html     # 管理页（列表/搜索/增删改/文件上传）
    ├── edit.html           # 编辑页（Markdown 原文编辑）
    └── view.html           # 查看页（渲染/原文切换 + KaTeX + High-lighting）
```

---

## 🚀 功能一览

- **文件系统存储**：每篇笔记独立保存为 `notes/<标题>.md`  
- **增删改查**：  
  - 新建、重命名、删除（基于 AJAX + Bootstrap Modal）  
  - 编辑（Markdown 原文）  
  - 查看（渲染模式 / 原文模式切换）  
- **Markdown 渲染**：  
  - [markdown-it](https://github.com/markdown-it/markdown-it)  
  - [KaTeX](https://katex.org/) 数学公式  
  - [Highlight.js](https://highlightjs.org/) 代码高亮  
- **全文搜索**：子串匹配 + 最长公共子序列（LCS）智能排序  
- **文件上传与管理**：支持图片、音频、视频等常见格式；浏览器内预览/播放  
- **页面美化**：Bootstrap 5 + 自适应布局  
- **零数据库依赖**：无需额外安装 SQLite/PostgreSQL  

---

## 📦 安装与运行

1. 克隆仓库  
   ```bash
   git clone https://github.com/yourusername/flask-fs-notebook-app.git
   cd flask-fs-notebook-app
   ```

2. （可选）创建并激活虚拟环境  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. 安装依赖  
   ```bash
   pip install flask
   ```

4. 运行应用  
   ```bash
   python app.py
   ```

5. 打开浏览器访问  
   ```
   http://127.0.0.1:5000/management
   ```

> ⚠️ **安全提示**：请修改 `app.secret_key` 为你的随机字符串，以保证 Session/Flash 安全。

---

## ⚙️ 配置说明

已在 `app.py` 顶部集中配置，运行前可根据需求修改：

```python
# Flask Secret Key
app.secret_key = '请替换为你自己的随机字符串'

# 笔记 & 上传目录
NOTE_DIR   = 'notes'
UPLOAD_DIR = 'uploads'

# 允许上传的文件扩展名
ALLOWED_EXT = {'png','jpg','jpeg','gif','mp4','mp3','ogg'}
```

- `NOTE_DIR`、`UPLOAD_DIR`：可指向任意你喜欢的绝对或相对路径  
- `ALLOWED_EXT`：控制可上传文件类型，防止任意文件写入  

---

## 📈 部署指南

### 1. 使用 Gunicorn + Nginx

1. 安装 Gunicorn：
   ```bash
   pip install gunicorn
   ```
2. 在项目根目录执行：
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
3. Nginx 反向代理示例：
   ```nginx
   server {
       listen 80;
       server_name example.com;
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       location /uploads/ {
           alias /path/to/flask-fs-notebook-app/uploads/;
       }
   }
   ```

### 2. Docker 容器化

- Dockerfile 示例：
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY . .
  RUN pip install flask
  EXPOSE 5000
  CMD ["python", "app.py"]
  ```
- 构建与运行：
  ```bash
  docker build -t flask-fs-notebook-app .
  docker run -d -p 5000:5000 \
    -v $(pwd)/notes:/app/notes \
    -v $(pwd)/uploads:/app/uploads \
    flask-fs-notebook-app
  ```

### 3. 其它托管平台

- Heroku、DigitalOcean App Platform、AWS EC2、Azure 等，均可通过上述方式部署。

---

## 🤝 贡献指南

1. Fork 本仓库  
2. 新建分支：`git checkout -b feature/YourFeature`  
3. 提交改动：`git commit -m "Add some feature"`  
4. Push 分支：`git push origin feature/YourFeature`  
5. 发起 Pull Request  

所有贡献者均需遵守 [CODE OF CONDUCT](https://www.contributor-covenant.org/)。

---

## 📜 许可证

本项目采用 **GNU General Public License v3.0** (GPL-3.0) 许可协议，详细内容见 [LICENSE](LICENSE)。  
你可以自由地使用、复制、修改和分发本软件，但需在相同协议下发布衍生作品。

---

✨ 感谢你的使用！欢迎 Star ⭐ 和 PR 👍，一起让它更好！  
---  
Made with ❤️ and ☕ by [wangyifan]
