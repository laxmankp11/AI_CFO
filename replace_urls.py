import os

file_path = '/Users/apple/Documents/AICFO/index.html'

with open(file_path, 'r') as f:
    content = f.read()

# Insert the API_BASE_URL configurations right after <script>
config_str = """
    // API Configuration
    const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const LARAVEL_API_URL = IS_LOCAL ? 'http://127.0.0.1:8001/api' : 'https://api.yourdomain.com/api';
    const PYTHON_API_URL = IS_LOCAL ? 'http://127.0.0.1:8000/internal/v1' : 'https://ai.yourdomain.com/internal/v1';
"""

if "const LARAVEL_API_URL" not in content:
    content = content.replace('<script>', f'<script>\n{config_str}')

# Replace hardcoded Laravel APIs
content = content.replace("'http://127.0.0.1:8001/api", "LARAVEL_API_URL + '")
content = content.replace("`http://127.0.0.1:8001/api", "LARAVEL_API_URL + `")

# Replace hardcoded Python APIs
content = content.replace("'http://127.0.0.1:8000/internal/v1", "PYTHON_API_URL + '")
content = content.replace("`http://127.0.0.1:8000/internal/v1", "PYTHON_API_URL + `")

with open(file_path, 'w') as f:
    f.write(content)

print("Replaced all hardcoded URLs in index.html.")
