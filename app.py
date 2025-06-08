import os, shutil
from flask import (
    Flask, render_template, request, jsonify, url_for,
    redirect, send_from_directory, abort
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '换成你自己的随机字符串'

# 配置目录
NOTE_DIR = 'notes'
UPLOAD_DIR = 'uploads'
ALLOWED_EXT = set(['png','jpg','jpeg','gif','mp4','mp3','ogg'])

# 启动前确保目录存在
for d in (NOTE_DIR, UPLOAD_DIR):
    os.makedirs(d, exist_ok=True)

# 工具：安全的笔记文件路径
def note_path(title):
    fn = secure_filename(title) or 'untitled'
    return os.path.join(NOTE_DIR, f"{fn}.md")

# 列出所有笔记
def list_notes():
    items = []
    for fn in os.listdir(NOTE_DIR):
        if fn.lower().endswith('.md'):
            title = fn[:-3]
            with open(os.path.join(NOTE_DIR, fn), encoding='utf-8') as f:
                content = f.read()
            items.append({'title': title, 'content': content})
    # 按文件修改时间倒排
    items.sort(key=lambda x: os.path.getmtime(note_path(x['title'])), reverse=True)
    return items

# LCS 长度
def lcs(a, b):
    la, lb = len(a), len(b)
    dp = [[0]*(lb+1) for _ in range(la+1)]
    for i in range(la):
        for j in range(lb):
            if a[i]==b[j]:
                dp[i+1][j+1]=dp[i][j]+1
            else:
                dp[i+1][j+1]=max(dp[i][j+1], dp[i+1][j])
    return dp[la][lb]

@app.route('/')
def index():
    return redirect(url_for('management'))

# 管理页
@app.route('/management')
def management():
    notes = list_notes()
    return render_template('management.html', notes=notes)

# AJAX: 新建/重命名/删除
@app.route('/note/<action>', methods=['POST'])
def note_action(action):
    data = request.get_json(force=True)
    try:
        if action=='new':
            title = data.get('title','').strip()
            if not title: raise ValueError('标题不能为空')
            path = note_path(title)
            if os.path.exists(path): raise FileExistsError('已存在同名笔记')
            open(path,'w', encoding='utf-8').close()
        elif action=='rename':
            old = data.get('old','').strip()
            new = data.get('new','').strip()
            if not all([old,new]): raise ValueError('名称不能为空')
            oldp, newp = note_path(old), note_path(new)
            if not os.path.exists(oldp): raise FileNotFoundError('源文件不存在')
            if os.path.exists(newp): raise FileExistsError('目标笔记已存在')
            os.rename(oldp, newp)
        elif action=='delete':
            title = data.get('title','').strip()
            p = note_path(title)
            if os.path.exists(p):
                os.remove(p)
        else:
            raise ValueError('未知操作')
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400

# 编辑/保存笔记
@app.route('/edit/<title>', methods=['GET','POST'])
def edit(title):
    p = note_path(title)
    if request.method=='POST':
        content = request.form.get('content','')
        with open(p,'w', encoding='utf-8') as f:
            f.write(content)
        return redirect(url_for('view', title=title))
    if not os.path.exists(p):
        abort(404, '笔记不存在')
    with open(p, encoding='utf-8') as f:
        content = f.read()
    return render_template('edit.html', title=title, content=content)

# 查看笔记
@app.route('/view/<title>')
def view(title):
    mode = request.args.get('mode','render')
    p = note_path(title)
    if not os.path.exists(p):
        abort(404,'笔记不存在')
    with open(p, encoding='utf-8') as f:
        content = f.read()
    return render_template('view.html',
                           title=title,
                           content=content,
                           mode=mode)

# 搜索
@app.route('/search')
def search():
    q = request.args.get('q','').lower()
    results = []
    for note in list_notes():
        t, c = note['title'].lower(), note['content'].lower()
        if q in t or q in c:
            score = lcs(q,t)*2 + lcs(q,c)
            results.append({
                'title': note['title'],
                'snippet': note['content'][:100].replace('\n',' '),
                'score': score
            })
    # 排序
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(results)

# 上传文件
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if not f:
        return jsonify(ok=False, error='未选择文件'), 400
    fn = secure_filename(f.filename)
    ext = fn.rsplit('.',1)[-1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify(ok=False, error='不支持的文件类型'), 400
    dst = os.path.join(UPLOAD_DIR, fn)
    f.save(dst)
    return jsonify(ok=True, url=url_for('uploaded_file', filename=fn))

# 列出上传文件
@app.route('/files')
def files():
    fl = []
    for fn in os.listdir(UPLOAD_DIR):
        fl.append({'name': fn, 'url': url_for('uploaded_file', filename=fn)})
    return jsonify(fl)

# 访问静态上传文件
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__=='__main__':
    app.run(debug=True)
