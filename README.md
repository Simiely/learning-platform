# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django + Alpine.js** 的幼儿识字/认知闪卡平台，支持 **浏览、卡片、练习** 三种学习模式，专为触屏（iPad / iPhone）设计，无需登录即可使用。支持 41 种动物中英文对照学习，配三语自动发音。

## 功能特性

- **浏览模式**：拼音排序的卡片网格，点击弹出全屏详情（支持图片缩放 + 前后翻页）+ 自动发音
- **卡片模式**：全屏沉浸式翻卡，随机起始 + 拼音排序，图片缩放（滚轮/双指），进场自动播放中英文
- **练习模式**：看图选词，即时反馈，10 题一组不重复。答对撒花 + 音效，答错柔和提示 + 显示正确答案
- **三语发音**：中文名称 / 英文名称 / 科普知识（中文），自动连播，每只动物独立音频
- **智能配色**：浏览方块背景基于 emoji 平均色动态生成（Pillow + NumPy）
- **三态主题**：深色 → 浅色 → 自动（跟随系统），偏好记忆到 localStorage
- **图片焦点**：每张图片手动校准视觉中心，iPhone / iPad 两套独立焦点，动物脸部始终可见
- **账号系统**：注册 / 登录 / 学习进度追踪（可选），未登录也能用全部功能

## 快速开始

```bash
git clone https://github.com/Simiely/learning-platform.git
cd learning-platform
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8000
```

打开 `http://localhost:8000` 即可使用。

## 使用方法

1. 首页点击「动物」进入，三种模式切换（页面顶部模式栏）：
   - **浏览** `/category/animals/`：方块网格 → 点击进入全屏弹窗（可前后翻页、点图缩放、自动发音）
   - **卡片** `/category/animals/cards/`：左右按钮翻页，随机起始，进场自动播放中英文
   - **练习** `/category/animals/quiz/`：看图选词，10 题一组，答对有礼花特效
2. 点击中文 / 英文 / 科普文字行即可播放对应语音
3. 右上角按钮切换主题：☀️ 深色 → 🌙 浅色 → 🌓 跟随系统
4. 浏览模式「再来一次」重置已查看状态（未登录用 localStorage 记录）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 4.2.x, Python 3.12+ |
| 前端 | Alpine.js 3.14（本地托管，不用 CDN）, 原生 CSS（CSS Variables） |
| 数据库 | SQLite（单文件，便于部署） |
| 音频生成 | edge-tts（Microsoft 神经网络语音，中文 Xiaoxiao / 英文 Jenny） |
| 图像处理 | Pillow, NumPy, OpenCV（headless） |
| 拼音排序 | pypinyin |
| 容器化 | Docker + GitHub Actions（自动构建推送 ghcr.io） |

## Docker 部署

支持一键 Docker 部署，镜像自动通过 GitHub Actions 构建推送。

```bash
docker compose up -d
```

访问 `http://服务器IP:2511`。数据持久化到 `/mnt/usb2/Configs/learning-platform/data`（db + media）。

**更新部署**：
```bash
docker compose pull && docker compose up -d
```

> `.env` 文件中需设置 `DJANGO_SECRET_KEY`，否则容器无法启动。

## 项目结构

```
learning-platform/
├── apps/core/                  # 核心应用
│   ├── models.py               # Category, Item, LearningProgress, QuizAttempt
│   ├── views.py                # 所有视图 + API（含 iPad 双焦点返回）
│   ├── image_utils.py          # emoji 取色 + 图片焦点检测
│   └── management/commands/
│       ├── seed_data.py        # 种子数据（41 只动物，含 iPhone/iPad 双套焦点）
│       ├── sync_positions.py   # 部署时同步图片焦点到数据库
│       ├── detect_centers.py   # OpenCV 自动检测焦点（不要用 --force）
│       └── ensure_media.py     # （已废弃，媒体从镜像 bundle 同步）
├── apps/users/                 # 用户模块
├── config/                     # Django 配置
├── templates/                  # HTML 模板
│   ├── base.html               # 公共布局
│   ├── category_browse.html    # 浏览模式（Emoji 方块网格）
│   ├── category_cards.html     # 卡片模式（含 card-zoom.js）
│   ├── category_quiz.html      # 练习模式（含 confetti + audio）
│   └── browse_popup.html       # 浏览弹窗
├── static/
│   ├── css/style.css           # 全局样式（CSS Variables，深/浅两套 token）
│   └── js/
│       ├── alpine.min.js       # Alpine.js 本地托管（不用 CDN！）
│       ├── theme.js            # 三态主题切换
│       ├── popup.js            # 浏览弹窗逻辑
│       └── card-zoom.js        # 卡片图片缩放
├── media/                      # 图片 + 音频素材（41 只动物，进 git）
├── ANIMALS.md                  # 动物数据主清单（含 iPhone/iPad 双焦点）
├── DEV.md                      # 开发笔记（详细踩坑记录）
├── Dockerfile
├── docker-entrypoint.sh        # 容器启动脚本（bootstrap）
├── docker-compose.yml
└── requirements.txt
```

## 数据清单

完整动物数据、图片焦点、科普知识详见 **[ANIMALS.md](./ANIMALS.md)**。目前包含 **41 种动物**，每只配有：

- 高清图片（手动裁剪构图）
- 中文 + 英文名称发音
- 中文科普知识发音
- iPhone / iPad 两套独立图片视觉焦点

## License

MIT
