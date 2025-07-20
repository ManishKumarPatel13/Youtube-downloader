# Example: Flask + React in one deployment

## Option A: Flask serves built React
```
your-project/
├── app.py                 # Flask backend
├── requirements.txt
├── package.json          # React dependencies
├── src/                  # React source
│   ├── components/
│   └── App.js
├── build/                # React build output
├── templates/2
│   └── index.html        # Template that loads React
└── static/
    └── build/            # React built files
```

## Flask app.py structure:
```python
from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__)

# Serve React app
@app.route('/')
def index():
    return render_template('index.html')

# Serve React static files
@app.route('/static/js/<path:filename>')
def react_js(filename):
    return send_from_directory('build/static/js', filename)

@app.route('/static/css/<path:filename>')
def react_css(filename):
    return send_from_directory('build/static/css', filename)

# Your API endpoints
@app.route('/api/data')
def api_data():
    return jsonify({"message": "Hello from backend"})
```

## Build process:
```bash
# Install both Python and Node dependencies
pip install -r requirements.txt
npm install
npm run build  # Creates optimized React build
```

## Option B: Template-Based (Like YouTube Project)
```
your-project/
├── app.py                 # Flask backend
├── routes.py             # API routes
├── requirements.txt
├── templates/
│   ├── base.html         # Base template
│   └── index.html        # Main page
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── app.js        # Vanilla JS or jQuery
```

## Templates use server-side rendering:
```html
<!-- templates/index.html -->
{% extends "base.html" %}
{% block content %}
<div id="app">
    <!-- Your UI components -->
    <div class="search-container">
        <input id="searchInput" type="text">
        <button onclick="searchData()">Search</button>
    </div>
    <div id="results"></div>
</div>

<script>
async function searchData() {
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: 'test'})
    });
    const data = await response.json();
    document.getElementById('results').innerHTML = data.results;
}
</script>
{% endblock %}
```

## Deployment Configurations

### Render (Python + Node)
```yaml
# render.yaml
services:
  - type: web
    name: fullstack-app
    env: python
    buildCommand: |
      pip install -r requirements.txt
      npm install
      npm run build
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: NODE_VERSION
        value: 18.17.0
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Railway
```json
// package.json
{
  "scripts": {
    "build": "npm run build-frontend && pip install -r requirements.txt",
    "build-frontend": "npm install && npm run build",
    "start": "gunicorn app:app"
  }
}
```

### Heroku
```
# Procfile
web: gunicorn app:app
release: npm run build

# .buildpacks
https://github.com/heroku/heroku-buildpack-nodejs
https://github.com/heroku/heroku-buildpack-python
```

## Advantages of Unified Deployment

### ✅ Benefits:
- **Single Domain**: No CORS issues
- **Simpler Deployment**: One build, one deploy
- **Cost Effective**: One hosting service instead of two
- **Better SEO**: Server-side rendering possible
- **Easier Debugging**: All logs in one place

### ❌ Limitations:
- **Less Flexibility**: Can't scale frontend/backend independently
- **Technology Lock-in**: Frontend tied to backend framework
- **Build Complexity**: Need to handle multiple build steps

## When to Use Each Approach

### Use Unified Deployment When:
- Building MVPs or smaller projects
- Want simple deployment process
- Cost is a primary concern
- Don't need independent scaling
- Team is comfortable with one tech stack

### Keep Separate When:
- Need independent scaling
- Different teams work on frontend/backend
- Using microservices architecture
- Need different deployment schedules
- Want technology flexibility
