# Flask 断点下载服务器设计

## 概述

使用 Flask 创建一个简单的 web 服务，支持断点下载，展示 downloads 文件夹下的文件列表，采用赛博朋克风格。

## 技术栈

- **后端**: Flask
- **前端**: Jinja2 模板 + 原生 CSS/JS
- **断点下载**: Flask `send_file` + `Range` 头处理

## 文件结构

```
share_server/
├── app.py              # Flask 主应用
├── downloads/          # 文件存放目录
├── static/
│   └── style.css       # 赛博朋克样式
├── templates/
│   └── index.html      # 首页模板
└── docs/
    └── plans/
        └── 2026-02-28-flask-download-server-design.md
```

## 核心功能

### 1. 断点下载

- 检测 `Range` 请求头
- 计算文件总大小和请求范围
- 返回 `206 Partial Content` + `Content-Range` 头
- 支持大文件流式传输

### 2. 文件列表

- 扫描 downloads 文件夹
- 显示文件名、大小、修改时间
- 根据文件扩展名显示对应图标
- 提供"下载"按钮和"复制链接"按钮

### 3. 赛博朋克样式

- 背景: `#0a0a0a` 深黑色
- 主色调: 霓虹紫 `#b026ff`、霓虹青 `#00f3ff`、霓虹粉 `#ff006e`
- 按钮发光效果: `box-shadow` + `text-shadow`
- 网格布局展示文件卡片

## 路由设计

| 路径 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 展示文件列表首页 |
| `/download/<filename>` | GET | 下载指定文件（支持断点续传） |

## 错误处理

- 文件不存在 → 404 错误页面
- 下载失败 → 友好错误提示
- 复制链接成功/失败 → 临时通知

## 设计日期

2026-02-28
