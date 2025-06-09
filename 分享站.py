import os
from flask import Flask, render_template_string, request, abort

# ---------------- Configuration ----------------
BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Define main types and their allowed extensions
TYPES = {
    'texts' : ['.txt', '.md', '.py', '.json'],
    'images': ['.png', '.jpg', '.jpeg', '.gif'],
    'videos': ['.mp4', '.mov', '.avi', '.webm'],
    'audios': ['.mp3', '.wav', '.ogg']
}
# -----------------------------------------------
app = Flask(__name__)
def scan_files():
    """
    Walk through static/<type>/** directories,
    organize files by type and subgroup,
    return a dict:
      {
        'texts': {
          'novels': [ {name, url, type, subgroup}, ... ],
          'code':   [ ... ],
        },
        ...
      }
    """
    result = {}
    for content_type, extensions in TYPES.items():
        base_folder = os.path.join(STATIC_DIR, content_type)
        subgroup_map = {}
        if os.path.isdir(base_folder):
            for dirpath, dirnames, filenames in os.walk(base_folder):
                # Calculate subgroup name relative to base_folder
                relative_path = os.path.relpath(dirpath, base_folder)
                subgroup = relative_path.replace(os.sep, '/')
                for filename in filenames:
                    ext = os.path.splitext(filename.lower())[1]
                    if ext in extensions:
                        # Build URL path under /static/
                        relpath = os.path.join(content_type, relative_path, filename).replace('\\', '/')
                        url = '/static/' + relpath
                        subgroup_map.setdefault(subgroup, []).append({
                            'name'    : filename,
                            'url'     : url,
                            'type'    : content_type,
                            'subgroup': subgroup
                        })
        result[content_type] = subgroup_map
    return result

# —— Home page ——
@app.route('/')
def index():
    data = scan_files()
    # Build statistics: count and subgroup list for each type
    stats = {
        content_type: {
            'count' : sum(len(files) for files in subgroup_map.values()),
            'groups': sorted(subgroup_map.keys())
        }
        for content_type, subgroup_map in data.items()
    }
    template = '''
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Content Overview</title>
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
            rel="stylesheet">
    </head>
    <body>
      <nav class="navbar navbar-dark bg-primary mb-4">
        <div class="container-fluid">
          <a class="navbar-brand" href="/">ShareSite</a>
        </div>
      </nav>
      <div class="container">
        <h1 class="mb-4">Content Overview</h1>
        <div class="row">
          {% for t, info in stats.items() %}
          <div class="col-md-3 mb-3">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ t.title() }}</h5>
                <p class="card-text">Total {{ info.count }} items</p>
                <a href="/list/{{t}}/" class="btn btn-outline-primary btn-sm">View All</a>
              </div>
            </div>
          </div>
          {% endfor %}
        </div>
      </div>
    </body>
    </html>
    '''
    return render_template_string(template, stats=stats)
# —— List page ——
@app.route('/list/<content_type>/', defaults={'subgroup': None})
@app.route('/list/<content_type>/<subgroup>')
def list_view(content_type, subgroup):
    if content_type not in TYPES:
        abort(404)
    data       = scan_files()
    subgroup_map = data.get(content_type, {})
    # Collect items in subgroup or all
    if subgroup:
        items = subgroup_map.get(subgroup, [])
    else:
        items = [item for files in subgroup_map.values() for item in files]
    # Keyword search
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered = []
        for item in items:
            if query in item['name'].lower():
                filtered.append(item)
                continue
            # If text, search inside file content
            if content_type == 'texts':
                filepath = os.path.join(STATIC_DIR, item['url'].lstrip('/static/'))
                try:
                    text_content = open(filepath, encoding='utf-8', errors='ignore').read().lower()
                    if query in text_content:
                        filtered.append(item)
                except:
                    pass
        items = filtered
    template = '''
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>List - {{content_type}}{% if subgroup %}/{{subgroup}}{% endif %}</title>
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
            rel="stylesheet">
    </head>
    <body>
      <nav class="navbar navbar-dark bg-primary mb-4">
        <div class="container-fluid">
          <a class="navbar-brand" href="/">ShareSite</a>
        </div>
      </nav>
      <div class="container">
        <h2 class="mb-3">{{content_type.title()}}{% if subgroup %}/ {{subgroup}}{% endif %}</h2>
        <form class="d-flex mb-3">
          <input class="form-control me-2" name="q" type="search"
                 placeholder="Search" value="{{request.args.get('q','')}}">
          <button class="btn btn-outline-success" type="submit">Search</button>
        </form>
        <div class="mb-3">
          <span>Subgroups:</span>
          <a href="/list/{{content_type}}/" class="btn btn-sm {% if not subgroup %}btn-primary{% else %}btn-outline-primary{% endif %}">
            All
          </a>
          {% for g in groups %}
          <a href="/list/{{content_type}}/{{g}}" class="btn btn-sm {% if g==subgroup %}btn-primary{% else %}btn-outline-primary{% endif %}">
            {{g}}
          </a>
          {% endfor %}
        </div>
        {% if items %}
        <ul class="list-group">
          {% for item in items %}
          <li class="list-group-item">
            <a href="/detail/{{item.type}}/{{item.subgroup}}/{{item.name}}">{{item.name}}</a>
          </li>
          {% endfor %}
        </ul>
        {% else %}
        <div class="alert alert-secondary">No matching items</div>
        {% endif %}
        <div class="mt-3">
          <a href="{{ request.referrer or '/' }}" class="btn btn-secondary">Back</a>
        </div>
      </div>
    </body>
    </html>
    '''
    return render_template_string(template,
                                  content_type=content_type,
                                  subgroup=subgroup,
                                  groups=sorted(subgroup_map.keys()),
                                  items=items)

# —— Detail page ——
@app.route('/detail/<content_type>/<subgroup>/<filename>')
def detail(content_type, subgroup, filename):
    data       = scan_files().get(content_type, {})
    items      = data.get(subgroup, [])
    for item in items:
        if item['name'] == filename:
            template = '''
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>{{item.name}}</title>
              <meta name="viewport" content="width=device-width,initial-scale=1">
              <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
                    rel="stylesheet">
            </head>
            <body>
              <nav class="navbar navbar-dark bg-primary mb-4">
                <div class="container-fluid">
                  <a class="navbar-brand" href="/">ShareSite</a>
                </div>
              </nav>
              <div class="container">
                <h2>{{item.name}}</h2>
                <p>Type: {{item.type.title()}} / {{item.subgroup}}</p><hr>
                <div class="mb-4">
                  {% if item.type=='texts' %}
                    <pre class="p-3 bg-light border" style="max-height:70vh;overflow:auto;">
{{ open('static/'+item.url.lstrip('/static/'), encoding='utf-8', errors='ignore').read() }}
                    </pre>
                  {% elif item.type=='images' %}
                    <img src="{{item.url}}" class="img-fluid" alt="{{item.name}}">
                  {% elif item.type=='videos' %}
                    <video controls class="w-100"><source src="{{item.url}}"></video>
                  {% elif item.type=='audios' %}
                    <audio controls class="w-100"><source src="{{item.url}}"></audio>
                  {% endif %}
                </div>
                <a href="{{ request.referrer or '/list/'+item.type+'/' }}" class="btn btn-secondary">Back</a>
              </div>
            </body>
            </html>
            '''
            return render_template_string(template, item=item)
    abort(404)
if __name__ == '__main__':
    app.run(debug=True)
