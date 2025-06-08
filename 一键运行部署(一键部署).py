import os
import time
import uuid
from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    url_for,
    send_from_directory,
    abort,
    render_template_string
)
from werkzeug.utils import secure_filename
# ----------------------------------------------------------------------
# Application Setup
# ----------------------------------------------------------------------
app = Flask(__name__)
# Replace with your own random secret key in production
app.secret_key = 'replace-with-your-own-random-string'
# ----------------------------------------------------------------------
# Configuration Constants
# ----------------------------------------------------------------------
NOTE_DIRECTORY = 'notes'                    # Directory for storing note files
UPLOAD_DIRECTORY = 'uploads'                # Directory for storing uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'ogg'}
ITEMS_PER_PAGE = 10                         # Number of notes per management page

# Ensure required directories exist
for directory in (NOTE_DIRECTORY, UPLOAD_DIRECTORY):
    os.makedirs(directory, exist_ok=True)
# ----------------------------------------------------------------------
# Templates as Multi-line Strings
# ----------------------------------------------------------------------
# Base HTML template with Bootstrap and blocks for title, head, content, scripts
BASE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}{% endblock %} - Cloud Notes</title>
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    rel="stylesheet">
  {% block head %}{% endblock %}
</head>
<body class="p-4 bg-light">
  <div class="container bg-white p-4 shadow-sm rounded">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ category }} alert-dismissible fade show">
            {{ message }}
            <button class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
  <script
    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">
  </script>
  {% block scripts %}{% endblock %}
</body>
</html>
'''

# Management page HTML: list, search, pagination, upload
MANAGEMENT_HTML = '''
{% extends 'base' %}
{% block title %}Manage Notes{% endblock %}
{% block content %}
<h1 class="mb-4">Manage Notes</h1>

<!-- Search Input -->
<div class="input-group mb-3">
  <input id="searchInput" type="text" class="form-control" placeholder="Search title or content…">
  <button id="searchButton" class="btn btn-outline-primary">🔍</button>
  <button id="clearButton" class="btn btn-outline-secondary">Clear</button>
</div>

<!-- Notes Table -->
<table class="table table-hover">
  <thead><tr><th>Title</th><th>Actions</th></tr></thead>
  <tbody id="noteList">
    {% for note in notes %}
    <tr data-title="{{ note.title }}">
      <td>{{ note.title }}</td>
      <td>
        <a href="{{ url_for('view_note', title=note.title) }}" target="_blank"
           class="btn btn-sm btn-success">View</a>
        <button class="btn btn-sm btn-warning renameButton">Rename</button>
        <button class="btn btn-sm btn-danger deleteButton">Delete</button>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<!-- Pagination Controls -->
<nav aria-label="Page navigation">
  <ul class="pagination">
    {% if page > 1 %}
    <li class="page-item">
      <a class="page-link" href="{{ url_for('manage', page=page-1) }}">Previous</a>
    </li>
    {% endif %}
    {% for p in range(1, total_pages + 1) %}
    <li class="page-item {% if p == page %}active{% endif %}">
      <a class="page-link" href="{{ url_for('manage', page=p) }}">{{ p }}</a>
    </li>
    {% endfor %}
    {% if page < total_pages %}
    <li class="page-item">
      <a class="page-link" href="{{ url_for('manage', page=page+1) }}">Next</a>
    </li>
    {% endif %}
  </ul>
</nav>

<button id="newButton" class="btn btn-primary mb-5">＋ New Note</button>

<hr>

<!-- File Upload Section -->
<h2 class="mt-4">File Upload</h2>
<form id="uploadForm" class="input-group mb-3" enctype="multipart/form-data">
  <input type="file" name="file" class="form-control">
  <button class="btn btn-info">Upload</button>
</form>
<ul id="fileList" class="list-group"></ul>
{% endblock %}

{% block scripts %}
<script>
// ----------------------------------------------------------------------
// JavaScript for Management Page
// ----------------------------------------------------------------------

// AJAX POST helper
function ajaxPost(url, data, onSuccess) {
  fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
  .then(response => {
    return response.json().then(json => {
      if (response.ok) {
        onSuccess(json);
      } else {
        throw new Error(json.error || 'Unknown error');
      }
    });
  })
  .catch(error => alert(error.message));
}

// Bootstrap Modal instance
let modal = new bootstrap.Modal(document.getElementById('modal'));
let actionType, originalTitle;

// Create new note
document.getElementById('newButton').onclick = () => {
  actionType = 'create';
  originalTitle = '';
  document.getElementById('modalTitle').innerText = 'New Note';
  document.getElementById('modalInput').value = '';
  modal.show();
};

// Rename note
document.querySelectorAll('.renameButton').forEach(button => {
  button.onclick = event => {
    actionType = 'rename';
    let row = event.target.closest('tr');
    originalTitle = row.dataset.title;
    document.getElementById('modalTitle').innerText = 'Rename Note';
    document.getElementById('modalInput').value = originalTitle;
    modal.show();
  };
});

// Delete note
document.querySelectorAll('.deleteButton').forEach(button => {
  button.onclick = event => {
    let title = event.target.closest('tr').dataset.title;
    if (confirm('Are you sure you want to delete this note?')) {
      ajaxPost('/note/delete', { title: title }, () => location.reload());
    }
  };
});

// Modal confirm action
document.getElementById('modalOk').onclick = event => {
  event.preventDefault();
  let newTitle = document.getElementById('modalInput').value.trim();
  if (!newTitle) {
    alert('Title cannot be empty');
    return;
  }
  if (actionType === 'create') {
    ajaxPost('/note/create', { title: newTitle }, () => location.reload());
  } else {
    ajaxPost('/note/rename', { old: originalTitle, new: newTitle }, () => location.reload());
  }
};

// Search notes
document.getElementById('searchButton').onclick = () => {
  let query = document.getElementById('searchInput').value.trim();
  if (!query) return;
  fetch('/search?q=' + encodeURIComponent(query))
    .then(res => res.json())
    .then(list => {
      let tbody = document.getElementById('noteList');
      tbody.innerHTML = '';
      list.forEach(item => {
        let tr = document.createElement('tr');
        tr.dataset.title = item.title;
        tr.innerHTML = `
          <td>${ item.title }</td>
          <td>
            <a class="btn btn-sm btn-success" target="_blank"
               href="/view/${ item.title }">View</a>
            <button class="btn btn-sm btn-warning renameButton">Rename</button>
            <button class="btn btn-sm btn-danger deleteButton">Delete</button>
          </td>`;
        tbody.appendChild(tr);
      });
      location.reload();  // reload to rebind events
    });
};

// Clear search results
document.getElementById('clearButton').onclick = () => location.reload();

// File upload form submission
document.getElementById('uploadForm').onsubmit = event => {
  event.preventDefault();
  let formData = new FormData(event.target);
  fetch('/upload', { method: 'POST', body: formData })
    .then(res => res.json().then(json => {
      if (res.ok) {
        loadFileList();
      } else {
        throw new Error(json.error);
      }
    }))
    .catch(err => alert(err.message));
};

// Load uploaded files into list
function loadFileList() {
  fetch('/files')
    .then(res => res.json())
    .then(files => {
      let list = document.getElementById('fileList');
      list.innerHTML = '';
      files.forEach(file => {
        let li = document.createElement('li');
        li.className = 'list-group-item';
        let ext = file.name.split('.').pop().toLowerCase();
        let html = `<a href="${ file.url }" target="_blank">${ file.name }</a>`;
        if (['mp4','mp3','ogg'].includes(ext)) {
          html += `<br><${ ext } controls
            src="${ file.url }"
            style="max-width:100%;margin-top:5px;">
          </${ ext }>`;
        }
        li.innerHTML = html;
        list.appendChild(li);
      });
    });
}

// Initial load of file list
loadFileList();
</script>

<!-- Modal Dialog for Create/Rename -->
<div class="modal fade" id="modal" tabindex="-1">
  <div class="modal-dialog">
    <form class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modalTitle">Title</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <input id="modalInput" class="form-control" placeholder="Enter note title">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary"
                data-bs-dismiss="modal">Cancel</button>
        <button id="modalOk" class="btn btn-primary">OK</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
'''

# Edit page HTML: textarea to edit note content
EDIT_HTML = '''
{% extends 'base' %}
{% block title %}Edit: {{ title }}{% endblock %}
{% block content %}
<h1 class="mb-4">Edit: {{ title }}</h1>
<form method="post">
  <textarea name="content" class="form-control" rows="20">{{ content }}</textarea>
  <div class="mt-3">
    <button class="btn btn-primary">Save</button>
    <a class="btn btn-secondary" href="{{ url_for('view_note', title=title) }}">Cancel</a>
  </div>
</form>
{% endblock %}
'''

# View page HTML: raw or rendered markdown with sanitizer
VIEW_HTML = '''
{% extends 'base' %}
{% block title %}View: {{ title }}{% endblock %}
{% block head %}
<link rel="stylesheet"
 href="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/katex.min.css">
<link rel="stylesheet"
 href="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github.min.css">
{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1>View: {{ title }}</h1>
  <div>
    <a class="btn btn-warning" href="{{ url_for('edit_note', title=title) }}">Edit</a>
    {% if mode == 'render' %}
      <a class="btn btn-secondary"
         href="{{ url_for('view_note', title=title, mode='raw') }}">Raw</a>
    {% else %}
      <a class="btn btn-secondary"
         href="{{ url_for('view_note', title=title, mode='render') }}">Rendered</a>
    {% endif %}
    <a class="btn btn-link" href="{{ url_for('manage') }}">Manage</a>
  </div>
</div>
{% if mode == 'raw' %}
  <pre class="border p-3">{{ content }}</pre>
{% else %}
  <div id="markdown" class="border p-4 rounded"></div>
{% endif %}
{% endblock %}
{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/markdown-it@13.0.1/dist/markdown-it.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/markdown-it-sanitizer/dist/markdown-it-sanitizer.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/markdown-it-katex@3.0.1/dist/markdown-it-katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/markdown-it-highlightjs@3.3.0/dist/markdown-it-highlightjs.min.js"></script>
<script>
// ----------------------------------------------------------------------
// Markdown Renderer Setup with Sanitizer
// ----------------------------------------------------------------------
const markdownRenderer = window.markdownit({
  html: true,
  linkify: true,
  typographer: true
})
  .use(window.markdownitSanitizer)  // Prevent XSS by sanitizing HTML
  .use(window.markdownitKatex)      // Support math formulas
  .use(window.markdownitHighlightjs); // Support code highlighting

// Render content into the 'markdown' container
const rawContent = {{ content|tojson }};
document.getElementById('markdown').innerHTML =
  markdownRenderer.render(rawContent);
</script>
{% endblock %}
'''

# Register base template for Jinja extends
app.jinja_loader.mapping = {
    'base': BASE_HTML
}

# ----------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------
def get_note_path(title: str) -> str:
    """
    Convert a note title into a secure file path under NOTE_DIRECTORY.
    """
    safe_name = secure_filename(title) or 'untitled'
    return os.path.join(NOTE_DIRECTORY, f"{safe_name}.md")

def list_all_notes() -> list:
    """
    Read all Markdown files in NOTE_DIRECTORY, return list of dicts:
    [{'title': ..., 'content': ..., 'mtime': ...}, ...] sorted by mtime descending.
    """
    notes = []
    for filename in os.listdir(NOTE_DIRECTORY):
        if not filename.lower().endswith('.md'):
            continue
        title = filename[:-3]
        path = os.path.join(NOTE_DIRECTORY, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        notes.append({
            'title': title,
            'content': content,
            'mtime': os.path.getmtime(path)
        })
    notes.sort(key=lambda x: x['mtime'], reverse=True)
    return notes

def longest_common_subsequence(a: str, b: str) -> int:
    """
    Compute length of the Longest Common Subsequence (LCS) between strings a and b.
    Used for search ranking.
    """
    len_a, len_b = len(a), len(b)
    dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]
    for i in range(len_a):
        for j in range(len_b):
            if a[i] == b[j]:
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])
    return dp[len_a][len_b]

# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route('/')
def index():
    """
    Redirect root URL to the management page.
    """
    return redirect(url_for('manage'))

@app.route('/management')
def manage():
    """
    Display the note management interface with pagination.
    """
    page = int(request.args.get('page', 1))
    all_notes = list_all_notes()
    total_count = len(all_notes)
    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paged_notes = all_notes[start:end]
    return render_template_string(
        MANAGEMENT_HTML,
        notes=paged_notes,
        page=page,
        total_pages=total_pages
    )

@app.route('/note/create', methods=['POST'])
def create_note():
    """
    AJAX endpoint to create a new note file with given title.
    """
    data = request.get_json(force=True)
    title = data.get('title', '').strip()
    if not title:
        return jsonify(ok=False, error='Title cannot be empty'), 400
    path = get_note_path(title)
    if os.path.exists(path):
        return jsonify(ok=False, error='Note already exists'), 400
    open(path, 'w', encoding='utf-8').close()
    return jsonify(ok=True)

@app.route('/note/rename', methods=['POST'])
def rename_note():
    """
    AJAX endpoint to rename a note from old title to new title.
    """
    data = request.get_json(force=True)
    old_title = data.get('old', '').strip()
    new_title = data.get('new', '').strip()
    if not old_title or not new_title:
        return jsonify(ok=False, error='Title cannot be empty'), 400
    old_path = get_note_path(old_title)
    new_path = get_note_path(new_title)
    if not os.path.exists(old_path):
        return jsonify(ok=False, error='Original note not found'), 404
    if os.path.exists(new_path):
        return jsonify(ok=False, error='Target note already exists'), 400
    os.rename(old_path, new_path)
    return jsonify(ok=True)

@app.route('/note/delete', methods=['POST'])
def delete_note():
    """
    AJAX endpoint to delete a note by title.
    """
    data = request.get_json(force=True)
    title = data.get('title', '').strip()
    path = get_note_path(title)
    if os.path.exists(path):
        os.remove(path)
        return jsonify(ok=True)
    return jsonify(ok=False, error='Note not found'), 404

@app.route('/edit/<title>', methods=['GET', 'POST'])
def edit_note(title):
    """
    GET: Render edit form with current content.
    POST: Save updated content and redirect to view.
    """
    path = get_note_path(title)
    if not os.path.exists(path):
        abort(404, 'Note not found')
    if request.method == 'POST':
        content = request.form.get('content', '')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return redirect(url_for('view_note', title=title))
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return render_template_string(EDIT_HTML, title=title, content=content)

@app.route('/view/<title>')
def view_note(title):
    """
    Display a note either as raw text or rendered Markdown.
    Mode controlled by 'mode' query parameter ('raw' or 'render').
    """
    mode = request.args.get('mode', 'render')
    path = get_note_path(title)
    if not os.path.exists(path):
        abort(404, 'Note not found')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return render_template_string(
        VIEW_HTML,
        title=title,
        content=content,
        mode=mode
    )

@app.route('/search')
def search_notes():
    """
    Search notes by query string across titles and contents.
    Return JSON list of {title, score} sorted by score desc.
    """
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    results = []
    for note in list_all_notes():
        title_lower = note['title'].lower()
        content_lower = note['content'].lower()
        in_title = query in title_lower
        in_content = query in content_lower
        if not (in_title or in_content):
            continue
        score = 0
        if in_title:
            score += longest_common_subsequence(query, title_lower) * 3
        if in_content:
            score += longest_common_subsequence(query, content_lower)
        results.append({'title': note['title'], 'score': score})
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(results)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload. Secure filename, check extension,
    avoid collisions by appending timestamp+UUID if needed.
    """
    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify(ok=False, error='No file selected'), 400
    original_filename = secure_filename(uploaded.filename)
    extension = original_filename.rsplit('.', 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify(ok=False, error='Unsupported file type'), 400

    # Build target path
    base_name, ext = os.path.splitext(original_filename)
    target_filename = original_filename
    target_path = os.path.join(UPLOAD_DIRECTORY, target_filename)

    # If file exists, append timestamp and UUID to filename
    if os.path.exists(target_path):
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex
        target_filename = f"{base_name}_{timestamp}_{unique_id}{ext}"
        target_path = os.path.join(UPLOAD_DIRECTORY, target_filename)

    # Save file and return its URL
    uploaded.save(target_path)
    file_url = url_for('uploaded_file', filename=target_filename)
    return jsonify(ok=True, url=file_url)

@app.route('/files')
def list_files():
    """
    Return JSON list of uploaded files with name and URL.
    """
    file_list = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        file_list.append({
            'name': filename,
            'url': url_for('uploaded_file', filename=filename)
        })
    return jsonify(file_list)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve an uploaded file by filename.
    """
    return send_from_directory(UPLOAD_DIRECTORY, filename)
# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # Run Flask development server (debug mode)
    app.run(debug=True)
