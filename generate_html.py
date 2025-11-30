import markdown
import re
import os

# Configuration
INPUT_FILE = "FULL_API_DOCUMENTATION_V2.md"
OUTPUT_FILE = "full_api_documentation_v2.html"

# CSS Styles
CSS = """
:root {
    --primary-color: #007bff;
    --sidebar-width: 280px;
    --header-height: 60px;
    --text-color: #333;
    --bg-color: #fff;
    --sidebar-bg: #f8f9fa;
    --border-color: #e9ecef;
    --code-bg: #f6f8fa;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    margin: 0;
    display: flex;
}

/* Sidebar */
.sidebar {
    width: var(--sidebar-width);
    height: 100vh;
    position: fixed;
    left: 0;
    top: 0;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border-color);
    overflow-y: auto;
    padding: 2rem 1rem;
    box-sizing: border-box;
}

.sidebar h3 {
    font-size: 0.85rem;
    text-transform: uppercase;
    color: #6c757d;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    padding-left: 0.5rem;
}

.sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.sidebar li {
    margin-bottom: 0.25rem;
}

.sidebar a {
    display: block;
    padding: 0.4rem 0.5rem;
    color: var(--text-color);
    text-decoration: none;
    font-size: 0.9rem;
    border-radius: 4px;
    transition: background 0.2s;
}

.sidebar a:hover {
    background: rgba(0,0,0,0.05);
    color: var(--primary-color);
}

.sidebar a.active {
    background: rgba(0, 123, 255, 0.1);
    color: var(--primary-color);
    font-weight: 500;
}

/* Main Content */
.main-content {
    margin-left: var(--sidebar-width);
    padding: 2rem 4rem;
    max-width: 900px;
    width: 100%;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-weight: 600;
    line-height: 1.25;
}

h1 { font-size: 2.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
h2 { font-size: 1.75rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3rem; margin-top: 3rem; }
h3 { font-size: 1.4rem; }
h4 { font-size: 1.1rem; }

a { color: var(--primary-color); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Code Blocks */
pre {
    background: var(--code-bg);
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.9rem;
    border: 1px solid var(--border-color);
}

code {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    background: rgba(0,0,0,0.05);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.9em;
}

pre code {
    background: transparent;
    padding: 0;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
}

th, td {
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    text-align: left;
}

th {
    background: var(--sidebar-bg);
    font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
    .sidebar {
        display: none; /* Simple mobile view for now */
    }
    .main-content {
        margin-left: 0;
        padding: 1rem;
    }
}
"""

def generate_toc(md_content):
    toc = []
    lines = md_content.split('\n')
    for line in lines:
        if line.startswith('## '):
            title = line.replace('## ', '').strip()
            anchor = title.lower().replace(' ', '-').replace('&', '').replace('/', '').replace('(', '').replace(')', '')
            toc.append({'level': 2, 'title': title, 'anchor': anchor})
        elif line.startswith('### '):
            title = line.replace('### ', '').strip()
            anchor = title.lower().replace(' ', '-').replace('&', '').replace('/', '').replace('(', '').replace(')', '')
            toc.append({'level': 3, 'title': title, 'anchor': anchor})
    return toc

def convert_to_html():
    # Read Markdown
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['fenced_code', 'tables', 'toc']
    )

    # Generate Custom TOC
    toc_items = generate_toc(md_content)
    toc_html = "<ul>"
    for item in toc_items:
        cls = "toc-h2" if item['level'] == 2 else "toc-h3"
        style = "padding-left: 1rem;" if item['level'] == 3 else ""
        toc_html += f'<li class="{cls}" style="{style}"><a href="#{item["anchor"]}">{item["title"]}</a></li>'
    toc_html += "</ul>"

    # HTML Template
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manning Agency API Documentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        {CSS}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div style="margin-bottom: 2rem; font-weight: bold; font-size: 1.2rem;">
            🚢 Manning API
        </div>
        {toc_html}
    </nav>
    <main class="main-content">
        {html_content}
    </main>
    <script>
        hljs.highlightAll();
        
        // Add IDs to headers for navigation
        document.querySelectorAll('h2, h3').forEach(header => {{
            const id = header.textContent.toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/(^-|-$)/g, '');
            header.id = id;
        }});
    </script>
</body>
</html>
"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        convert_to_html()
    except ImportError:
        print("Error: 'markdown' library not found. Please run: pip install markdown")
    except Exception as e:
        print(f"Error: {e}")
