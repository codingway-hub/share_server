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
