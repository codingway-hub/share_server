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

3. 访问 http://localhost:5001

## 断点下载

服务器支持 HTTP Range 请求，可实现断点续传。下载工具（如 wget、curl、浏览器下载管理器）会自动使用此功能。

## 自定义配置

修改 `app.py` 中的以下配置：

- `DOWNLOAD_FOLDER`: 下载文件存放目录
- `host`: 监听地址（默认 0.0.0.0）
- `port`: 监听端口（默认 5001）

## 技术栈

- Flask 3.0.0
- Jinja2
- 原生 CSS/JS
