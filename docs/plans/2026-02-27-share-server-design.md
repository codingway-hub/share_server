# Share Server - 赛博朋克文件共享服务器设计文档

**日期：** 2026-02-27
**类型：** 新项目

## 项目概述

局域网内个人设备间的快速文件和文字共享服务器，采用赛博朋克霓虹发光风格，支持断点续传。

## 需求总结

- **使用场景：** 个人设备间快速传输（类似 AirDrop）
- **界面：** 赛博朋克霓虹发光风格 Web UI
- **核心功能：** 文字便签（支持 Markdown）、文件传输（断点续传）、访问密码
- **技术栈：** Python 3 + Flask

## 系统架构

### 技术栈
- 后端：Python 3 + Flask
- 数据库：SQLite
- 前端：HTML + CSS + JavaScript（原生）
- 样式：霓虹发光主题（青色 #00f3ff、洋红 #ff00ff、紫色 #bd00ff）

### 目录结构
```
share_server/
├── app.py              # Flask 主应用
├── models.py           # 数据库模型
├── routes/             # 路由模块
│   ├── __init__.py
│   ├── files.py
│   ├── notes.py
│   └── auth.py
├── static/
│   ├── css/
│   │   └── style.css   # 赛博朋克样式
│   └── js/
│       └── app.js      # 前端逻辑
├── templates/
│   ├── index.html      # 主页
│   ├── upload.html     # 上传页
│   ├── files.html      # 文件列表
│   └── notes.html      # 便签列表
├── uploads/            # 文件存储目录
└── data/
    └── cyber_share.db  # SQLite 数据库
```

## 数据模型

### 文件表 (files)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| filename | TEXT | 原始文件名 |
| stored_path | TEXT | 存储路径 |
| file_size | INTEGER | 文件大小（字节） |
| password | TEXT | 访问密码（可选） |
| upload_time | TIMESTAMP | 上传时间 |
| downloads_count | INTEGER | 下载次数 |
| mime_type | TEXT | MIME 类型 |

### 便签表 (notes)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| title | TEXT | 便签标题 |
| content | TEXT | Markdown 内容 |
| password | TEXT | 访问密码（可选） |
| created_time | TIMESTAMP | 创建时间 |
| expires_at | TIMESTAMP | 过期时间 |

## API 路由设计

### 文件相关
- `POST /api/upload` - 上传文件（支持断点续传）
- `GET /api/files` - 获取文件列表
- `GET /api/files/<id>` - 下载文件（支持 Range 请求实现断点）
- `DELETE /api/files/<id>` - 删除文件

### 便签相关
- `POST /api/notes` - 创建便签
- `GET /api/notes` - 获取便签列表
- `GET /api/notes/<id>` - 获取便签内容
- `DELETE /api/notes/<id>` - 删除便签

### 认证相关
- `POST /api/verify-password` - 验证访问密码

### 静态页面
- `GET /` - 主页
- `GET /upload` - 上传页面
- `GET /files` - 文件列表页面
- `GET /notes` - 便签页面

## 断点续传实现

### 服务器端
使用 HTTP Range 请求支持断点续传：
- 检查 `Range` 请求头
- 解析 `bytes=start-end` 格式
- 返回 `206 Partial Content` 状态码
- 添加 `Content-Range` 和 `Accept-Ranges` 响应头

### 客户端
浏览器原生支持断点续传，自动处理 Range 请求

## 界面设计

### 色彩方案
- 主色调：青色 `#00f3ff`
- 辅助色：洋红 `#ff00ff`、紫色 `#bd00ff`
- 背景：深色 `#0a0a12`
- 文字：白色/浅灰色

### 视觉效果
- 发光边框和按钮（box-shadow）
- 扫描线背景效果
- 科技感字体（Orbitron 或类似）
- 渐变动画

### 页面布局

#### 主页
- 霓虹 Logo
- 功能入口卡片（上传、文件、便签）

#### 上传页
- 拖拽上传区
- 密码设置选项
- 上传进度显示

#### 文件列表
- 卡片式布局
- 文件名、大小、时间显示
- 下载/删除按钮

#### 便签列表
- Markdown 预览
- 编辑/删除按钮
