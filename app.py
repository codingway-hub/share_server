from flask import Flask, render_template, send_file, request
import os
from datetime import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.abspath('downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def get_file_info(filename):
    """获取文件信息"""
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    try:
        stat = os.stat(filepath)
    except (FileNotFoundError, OSError):
        # 文件可能在读取时被删除，返回 None
        return None
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

    file_list = sorted([info for f in files
                        if (info := get_file_info(f)) is not None],
                      key=lambda x: x['name'])

    return render_template('index.html', files=file_list)

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
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
