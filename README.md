# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django** 的幼儿识字 / 认知闪卡平台，支持**浏览、卡片、练习**三种学习模式，界面专为触屏（iPad / 手机）设计，支持深色 / 浅色主题。

## 功能特性

- **浏览模式**：按拼音首字母排序的动物卡片网格，emoji + 中英文名，点击弹出详情与发音
- **卡片模式**：全屏沉浸式卡片，图片自适应 + 进场自动播放中英文发音 + 上一张 / 随机 / 下一张切换
- **练习模式**：看图选词，即时反馈（正确高亮、错误标红、其余淡化）
- **三语发音**：中文 / 英文 / 科普语音，支持自动连播（中文 → 1 秒后 → 英文）
- **智能配色**：浏览方块背景 = emoji 平均色 + 70% 黑；图片区背景 = 图片平均色 + 60% 黑
- **深色 / 浅色模式**：右上角一键切换，偏好记忆到 `localStorage`
- **账号系统**：注册 / 登录 / 学习进度追踪

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 4.2.x, Python 3.13 |
| 前端 | Alpine.js（CDN 引入）, 原生 CSS（CSS Variables） |
| 数据库 | SQLite（开发） |
| 图片处理 | Pillow, NumPy |
| 拼音排序 | pypinyin |

## 部署指南

### 环境要求

- **Python**：3.13.x（开发实测，其他 3.x 未验证）
- **pip**：随 Python 自带
- **操作系统**：Windows / macOS / Linux 均可（路径差异见下）
- **网络**：首次 `pip install` 需联网拉取依赖

> ⚠️ **依赖完整性**：`numpy`、`pypinyin` 与 `opencv-python-headless` 都是 `views.py` 实际 import 的包（`cv2` 用于图片焦点检测），**必须安装**，已写入 `requirements.txt`。若用旧版 `requirements.txt` 漏装，启动会直接 `ModuleNotFoundError`。

### 方式一：本地 / 局域网部署（推荐首次运行）

```bash
# 1. 拉取代码
git clone <repo-url> learning-platform
cd learning-platform

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows (PowerShell / CMD)

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库（生成 db.sqlite3，此文件不进 git）
python manage.py migrate

# 5. 加载示例数据（21 个动物 + 图片 + 中/英/科普音频）
python manage.py seed_data

# 6.（可选）创建管理员
python manage.py createsuperuser  # 访问 /admin/ 管理卡片内容

# 7. 启动
python manage.py runserver 0.0.0.0:8000   # 局域网内设备访问 http://<本机IP>:8000
```

**到这里就完成了**。浏览器打开 `http://localhost:8000` 即可使用，无需任何额外配置。

### 方式二：生产部署要点

本项目开发用 SQLite + Django 自带服务器，若要对外正式部署，注意以下几点：

| 项目 | 说明 |
|------|------|
| `DEBUG` | 必须设为 `False`（在 `config/settings.py`）。`DEBUG=True` 时 Django 会自动托管 `media/`，关闭后**媒体文件不会自动提供**，需另行配置。 |
| `ALLOWED_HOSTS` | `DEBUG=False` 时必须填写你的域名 / IP，否则请求被拒。 |
| 静态文件 | `python manage.py collectstatic` 收集到 `STATIC_ROOT`，由 Web 服务器（Nginx / Caddy）或 CDN 提供。 |
| 媒体文件 | `media/` **不会被 `collectstatic` 收集**，需由 Web 服务器直接映射提供（如 Nginx `location /media/`）。 |
| 应用服务器 | 可用 `gunicorn config.wsgi:application` 替代 `runserver`。 |
| 简单场景 | 若仅家庭 / 局域网内 iPad 使用，保留 `DEBUG=True` + `runserver` 即可，最省心。 |

### 部署检查清单（避免出错）

- [ ] `python --version` 是 3.13.x
- [ ] 已 `pip install -r requirements.txt` 且**无报错**（确认 numpy / pypinyin / opencv-python-headless 已装）
- [ ] 已执行 `python manage.py migrate`
- [ ] 已执行 `python manage.py seed_data`（看到 "Created 21 items" 之类输出）
- [ ] 若 `seed_data` 中途报错，**重跑即可**（已幂等，不会重复创建或产生随机后缀脏文件）
- [ ] `media/` 目录存在 `images/`、`audio/`、`audio_en/`、`audio_fact/` 且文件名是纯英文名（如 `lion.jpg`、`lion.mp3`）
- [ ] 启动后访问 `/media/audio/lion.mp3` 返回 200（验证音频可正常加载）

### 常见部署错误速查

| 现象 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'numpy' / 'cv2' / 'pypinyin'` | 依赖漏装 | `pip install -r requirements.txt`（已含全部必需依赖） |
| `seed_data` 报 `ValueError: ... bg_color` | 旧版 seed 给已删除字段赋值 | 用仓库最新 `seed_data.py`（已修复） |
| 发声按钮 404 / 无声音 | DB 字段名与磁盘文件名不一致 | 重跑 `seed_data`（已确定性写入纯名）；详见 **DEV.md**「音频 404」 |
| 页面样式全乱 / 不更新 | 浏览器缓存旧 CSS | 已用 `style.css?v=<日期>` 版本号，硬刷新（Ctrl/Cmd+Shift+R） |
| 白底变全黑 | iPad「智能反转」开启 | 关闭 设置 → 辅助功能 → 显示与文字大小 → 智能反转 |
| 管理后台 404 | 未 `createsuperuser` 或未 `migrate` | 先 `migrate` 再 `createsuperuser` |



## Docker 一键部署（推荐）

一条命令即可拉起可用服务：**自动建库 → 下载素材 → 灌入示例数据 → 建默认账号 → 启动**。

```bash
# 所有配置已直接写在 docker-compose.yml 中，无需 .env，直接构建并启动：
docker compose up --build -d
```

启动后访问 `http://localhost:2511`，用默认账号 `admin / admin1234` 登录。

### 工作原理

| 环节 | 说明 |
|------|------|
| `docker-compose.yml` | 所有配置（代码路径、数据路径、管理员账号密码、DEBUG 等）已直接写死在文件内，**无需 `.env`** |
| `docker-entrypoint.sh` | 启动顺序：migrate → ensure_media →（首次）seed_data → 自动建管理员 → gunicorn |
| `ensure_media` 命令 | 首次启动从 `MEDIA_SOURCE_URL`（默认本仓库 tarball）下载并解压 `media/` 到卷；已存在则跳过，重启不重复下载 |
| 代码/数据位置 | 代码 `/mnt/usb2/Configs/learning-platform/app`、数据 `/mnt/usb2/Configs/learning-platform/data`（绑定挂载持久化 db 与 media，重建镜像不丢） |

### 自定义

- **代码位置**：compose 中 `build.context` 已写死为 `/mnt/usb2/Configs/learning-platform/app`（父级目录下的 `app/` 子目录，仓库克隆到这里）。改完代码后 `docker compose up --build` 即生效。
- **数据位置**：compose 中 `volumes` 已写死为 `/mnt/usb2/Configs/learning-platform/data`（db 与 media）。代码与数据共享同一个父级目录 `/mnt/usb2/Configs/learning-platform/`，便于管理。重建镜像数据不丢；想彻底重置就删掉该目录。
- **默认账号**：compose 中 `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD` 已写死为 `admin / admin1234`（仅首次启动生效；之后改密码用 `docker compose exec web python manage.py changepassword admin`）。
- **素材来源**：compose 中 `MEDIA_SOURCE_URL` 可改成你自己的 COS / S3 直链（任意含顶层 `media/` 目录的 `tar.gz`）。
- **重新灌数据**：`docker compose exec web python manage.py seed_data`（注意会清空并重建条目）。
- **生产环境**：将 `DJANGO_DEBUG` 设为 `False`，并另行用 Nginx/Whitenoise 托管媒体与静态文件。

## 使用方法

1. 首页选择分类（当前为「动物」），进入三种学习模式：
   - **浏览**：网格浏览，点方块弹出大图与发音
   - **卡片**：左右滑动 / 点 ‹ › 翻页，🎲 随机，点击中 / 英 / 科普三行即可发声
   - **练习**：看图片选正确词语，答完看反馈
2. 右上角 🌙 / ☀️ 按钮切换深色 / 浅色模式。
3. 发声按钮无声音时，先确认设备未静音、且 iPad 未开启「智能反转」（见 DEV.md）。

## 项目结构

```
learning-platform/
├── apps/
│   ├── core/          # 核心应用（Category、Item 模型）
│   │   ├── models.py
│   │   ├── views.py            # 视图 + emoji 取色 + 图片平均色 + 图片焦点检测
│   │   ├── admin.py
│   │   └── management/commands/seed_data.py
│   └── users/         # 用户（注册 / 登录 / 进度）
├── config/            # Django 项目配置
├── templates/         # HTML 模板（base / index / 三种模式 / 弹窗）
├── static/css/style.css   # 全局样式（:root 设计变量 + 深色模式 token）
├── media/             # 图片与音频素材（已纳入版本管理，见下）
└── requirements.txt
```

## 媒体资源与音频

- 素材位于 `media/`（子目录 `images` / `audio` / `audio_en` / `audio_fact`），**已纳入 git 版本管理**。
- 三种音频通过 `Item.audio / audio_en / audio_fact` 存储，前端用 `/media/` + 字段名拼接播放。
- `seed_data` 现已**幂等且确定性**：无论是否已有 media 文件，始终写入规范纯名（如 `audio/lion.mp3`）并清理历史随机后缀孤儿文件，保证数据库字段名与磁盘一致。全新 clone 后直接 `migrate` + `seed_data` 即可，无需先清空 `media`。详见 **DEV.md**「音频 404」一节了解原理。

## 开发笔记

关键问题排查（音频 404、iPad 白变黑、CSS 缓存、本机 venv 路径、深色模式变量体系等）统一记录在 **DEV.md**，遇到同类问题先查那里。

## License

MIT
