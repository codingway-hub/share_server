# Flask 断点下载服务器实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 使用 Flask 创建一个支持断点下载的 web 服务，展示 downloads 文件夹文件列表，采用赛博朋克风格。

**Architecture:** Flask 应用使用 Jinja2 模板渲染文件列表页面，断点下载通过处理 Range 请求头实现，赛博朋克样式使用原生 CSS 霓虹效果。

**Tech Stack:** Flask, Jinja2, 原生 CSS/JS

---

### Task 1: 创建项目基础结构

**Files:**
- Create: `app.py`
- Create: `static/style.css`
- Create: `templates/index.html`
- Create: `requirements.txt`

**Step 1: 创建 requirements.txt**

```bash
cat > requirements.txt << 'EOF'
Flask==3.0.0
Werkzeug==3.0.1
EOF
```

**Step 2: 创建基础的 app.py**

```python
from flask import Flask, send_file, request
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

@app.route('/')
def index():
    return "Hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Step 3: 创建基础的 index.html**

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>下载中心</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>下载中心</h1>
    </div>
</body>
</html>
```

**Step 4: 创建基础的 style.css**

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: #0a0a0a;
    font-family: 'Courier New', monospace;
    color: #00f3ff;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}

h1 {
    text-align: center;
    font-size: 2.5rem;
    text-shadow: 0 0 20px #00f3ff;
    margin-bottom: 40px;
}
```

**Step 5: 安装依赖并测试运行**

```bash
pip install -r requirements.txt
python app.py &
sleep 2
curl http://localhost:5000/
pkill -f "python app.py"
```

**Step 6: 提交**

```bash
git add app.py static/style.css templates/index.html requirements.txt
git commit -m "feat: create basic Flask project structure"
```

---

### Task 2: 实现文件列表功能

**Files:**
- Modify: `app.py`
- Modify: `templates/index.html`
- Modify: `static/style.css`

**Step 1: 修改 app.py 添加文件扫描逻辑**

```python
from flask import Flask, render_template, send_file, request
import os
from datetime import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.abspath('downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def get_file_info(filename):
    """获取文件信息"""
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    stat = os.stat(filepath)
    size = stat.st_size
    mtime = datetime.fromtimestamp(stat.st_mtime)
    ext = os.path.splitext(filename)[1].lower()

    # 文件类型图标映射
    icon_map = {
        '.pdf': '📄',
        '.doc': '📝', '.docx': '📝',
        '.xls': '📊', '.xlsx': '📊',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬',
        '.mp3': '🎵', '.wav': '🎵',
        '.zip': '📦', '.rar': '📦', '.7z': '📦',
        '.txt': '📃',
    }

    icon = icon_map.get(ext, '📁')

    return {
        'name': filename,
        'size': format_size(size),
        'mtime': mtime.strftime('%Y-%m-%d %H:%M'),
        'icon': icon
    }

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@app.route('/')
def index():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    files = [f for f in os.listdir(DOWNLOAD_FOLDER)
             if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))]

    file_list = sorted([get_file_info(f) for f in files],
                      key=lambda x: x['name'])

    return render_template('index.html', files=file_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Step 2: 修改 index.html 添加文件列表**

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>下载中心</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>下载中心</h1>

        {% if files %}
        <div class="file-grid">
            {% for file in files %}
            <div class="file-card">
                <div class="file-icon">{{ file.icon }}</div>
                <div class="file-info">
                    <h3 class="file-name">{{ file.name }}</h3>
                    <div class="file-meta">
                        <span class="file-size">{{ file.size }}</span>
                        <span class="file-mtime">{{ file.mtime }}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-primary" onclick="downloadFile('{{ file.name }}')">
                        ⬇️ 下载
                    </button>
                    <button class="btn btn-secondary" onclick="copyLink('{{ file.name }}')">
                        🔗 复制链接
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <p>暂无文件，请将文件放入 downloads 文件夹</p>
        </div>
        {% endif %}
    </div>

    <div id="notification" class="notification"></div>

    <script>
        function downloadFile(filename) {
            window.location.href = `/download/${filename}`;
        }

        function copyLink(filename) {
            const link = `${window.location.origin}/download/${filename}`;
            navigator.clipboard.writeText(link).then(() => {
                showNotification('链接已复制到剪贴板');
            }).catch(() => {
                showNotification('复制失败，请手动复制');
            });
        }

        function showNotification(message) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
            }, 2000);
        }
    </script>
</body>
</html>
```

**Step 3: 更新 style.css 添加文件列表样式**

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: #0a0a0a;
    font-family: 'Courier New', monospace;
    color: #00f3ff;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}

h1 {
    text-align: center;
    font-size: 2.5rem;
    text-shadow: 0 0 20px #00f3ff;
    margin-bottom: 40px;
    letter-spacing: 4px;
}

.file-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

.file-card {
    background: linear-gradient(135deg, rgba(176, 38, 255, 0.1), rgba(0, 243, 255, 0.05));
    border: 1px solid rgba(176, 38, 255, 0.3);
    border-radius: 10px;
    padding: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 0 10px rgba(176, 38, 255, 0.1);
}

.file-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 20px rgba(176, 38, 255, 0.3);
    border-color: #00f3ff;
}

.file-icon {
    font-size: 3rem;
    text-align: center;
    margin-bottom: 15px;
}

.file-name {
    font-size: 1.1rem;
    margin-bottom: 10px;
    word-break: break-all;
    color: #ff006e;
    text-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
}

.file-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #888;
    margin-bottom: 15px;
}

.file-actions {
    display: flex;
    gap: 10px;
}

.btn {
    flex: 1;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    font-family: inherit;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.btn-primary {
    background: linear-gradient(135deg, #b026ff, #00f3ff);
    color: #fff;
    box-shadow: 0 0 15px rgba(176, 38, 255, 0.5);
}

.btn-primary:hover {
    box-shadow: 0 0 25px rgba(176, 38, 255, 0.8);
    transform: scale(1.05);
}

.btn-secondary {
    background: transparent;
    border: 1px solid #b026ff;
    color: #b026ff;
    box-shadow: 0 0 10px rgba(176, 38, 255, 0.3);
}

.btn-secondary:hover {
    background: rgba(176, 38, 255, 0.2);
    box-shadow: 0 0 15px rgba(176, 38, 255, 0.6);
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #666;
}

.empty-state p {
    font-size: 1.2rem;
}

.notification {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: linear-gradient(135deg, #b026ff, #00f3ff);
    color: #fff;
    padding: 15px 30px;
    border-radius: 5px;
    box-shadow: 0 0 20px rgba(176, 38, 255, 0.6);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 1000;
}

.notification.show {
    transform: translateY(0);
    opacity: 1;
}

@media (max-width: 768px) {
    h1 {
        font-size: 1.8rem;
    }

    .file-grid {
        grid-template-columns: 1fr;
    }
}
```

**Step 4: 创建测试文件并测试**

```bash
# 创建测试文件
echo "test content" > downloads/test.txt
echo '{"key": "value"}' > downloads/test.json
# 启动服务器
python app.py &
sleep 2
# 测试首页
curl -s http://localhost:5000/ | grep "下载中心"
pkill -f "python app.py"
```

**Step 5: 提交**

```bash
git add app.py templates/index.html static/style.css
git commit -m "feat: implement file list display with cyberpunk style"
```

---

### Task 3: 实现断点下载功能

**Files:**
- Modify: `app.py`

**Step 1: 添加断点下载路由**

在 app.py 的 `@app.route('/')` 之后添加：

```python
@app.route('/download/<filename>')
def download(filename):
    """支持断点续传的下载接口"""
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    # 安全检查：防止路径遍历攻击
    if '..' in filename or filename.startswith('/'):
        return "Invalid filename", 400

    if not os.path.exists(filepath):
        return "File not found", 404

    if not os.path.isfile(filepath):
        return "Not a file", 400

    file_size = os.path.getsize(filepath)
    range_header = request.headers.get('Range')

    if range_header:
        # 处理断点续传请求
        # Range: bytes=start-end
        try:
            byte_range = range_header.replace('bytes=', '').split('-')
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if byte_range[1] else file_size - 1

            # 验证范围
            if start < 0 or end >= file_size or start > end:
                return "Invalid range", 416

            chunk_size = end - start + 1

            def generate():
                with open(filepath, 'rb') as f:
                    f.seek(start)
                    remaining = chunk_size
                    while remaining > 0:
                        chunk_size_read = min(8192, remaining)
                        data = f.read(chunk_size_read)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            response = app.response_class(
                generate(),
                206,
                direct_passthrough=True,
                mimetype='application/octet-stream'
            )
            response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(chunk_size))
        except (ValueError, IndexError):
            return "Invalid range format", 400
    else:
        # 完整文件下载
        response = send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        response.headers.add('Accept-Ranges', 'bytes')

    response.headers.add('Content-Disposition', f'attachment; filename="{filename}"')
    return response
```

**Step 2: 测试完整下载**

```bash
# 创建测试文件
dd if=/dev/zero of=downloads/test_file.bin bs=1024 count=100

python app.py &
sleep 2

# 测试完整下载
curl -s -o /tmp/test_full.bin http://localhost:5000/download/test_file.bin
ls -lh /tmp/test_full.bin

# 清理
rm /tmp/test_full.bin
pkill -f "python app.py"
```

**Step 3: 测试断点下载**

```bash
python app.py &
sleep 2

# 测试前 10KB
curl -s -H "Range: bytes=0-10239" -o /tmp/test_part1.bin http://localhost:5000/download/test_file.bin

# 测试断点续传
curl -s -H "Range: bytes=10240-" -o /tmp/test_part2.bin http://localhost:5000/download/test_file.bin

# 验证文件大小
echo "Part1 size:"
ls -lh /tmp/test_part1.bin
echo "Part2 size:"
ls -lh /tmp/test_part2.bin

# 清理
rm /tmp/test_part*.bin
pkill -f "python app.py"
```

**Step 4: 提交**

```bash
git add app.py
git commit -m "feat: implement resumable download with Range header support"
```

---

### Task 4: 添加 README 文档

**Files:**
- Create: `README.md`

**Step 1: 创建 README.md**

```markdown
# Flask 断点下载服务器

一个简单的 Flask web 服务，支持断点下载，采用赛博朋克风格。

## 功能特性

- 支持断点续传下载
- 文件列表展示
- 一键复制下载链接
- 赛博朋克霓虹风格界面

## 安装

```bash
pip install -r requirements.txt
```

## 使用

1. 将需要分享的文件放入 `downloads` 文件夹
2. 启动服务器：

```bash
python app.py
```

3. 访问 http://localhost:5000

## 断点下载

服务器支持 HTTP Range 请求，可实现断点续传。下载工具（如 wget、curl、浏览器下载管理器）会自动使用此功能。

## 自定义配置

修改 `app.py` 中的以下配置：

- `DOWNLOAD_FOLDER`: 下载文件存放目录
- `host`: 监听地址（默认 0.0.0.0）
- `port`: 监听端口（默认 5000）

## 技术栈

- Flask 3.0.0
- Jinja2
- 原生 CSS/JS
```

**Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README"
```

---

### Task 5: 清理和验证

**Step 1: 清理测试文件**

```bash
rm downloads/test.txt downloads/test.json downloads/test_file.bin
```

**Step 2: 最终验证**

```bash
# 启动服务器
python app.py &
sleep 2

# 测试首页
curl -s http://localhost:5000/ | head -20

# 停止服务器
pkill -f "python app.py"
```

**Step 3: 提交**

```bash
git add -A
git commit -m "chore: clean up test files and finalize project"
```

---

## 完成

所有任务完成后，你将拥有一个功能完整的 Flask 断点下载服务器，具有以下特性：

1. 赛博朋克风格的文件列表界面
2. 支持断点续传的下载功能
3. 一键复制下载链接
4. 根据文件类型显示对应图标
