# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django** 的幼儿识字 / 认知闪卡平台，支持**浏览、卡片、练习**三种学习模式，专为触屏（iPad / 手机）设计，无需登录即可使用。

## 功能特性

- **浏览模式**：拼音排序的动物卡片网格，点击弹出全屏详情（支持图片缩放 + 前后翻页）+ 自动发音
- **卡片模式**：全屏沉浸式卡片，随机起始 + 拼音排序 + 前后翻页，图片缩放（滚轮/双指），进场自动播放中英文发音
- **练习模式**：看图选词，即时反馈，10 题一组，题目不重复。答对撒花特效 + 自动朗读中英文。结果页大字报排版
- **三语发音**：中文 / 英文 / 科普语音，自动连播
- **智能配色**：浏览方块背景基于 emoji 平均色动态生成
- **三态主题**：深色 → 浅色 → 自动（跟随系统），偏好记忆到 localStorage
- **图片焦点**：手动校准的视觉中心，卡片模式自动上偏补偿，让动物脸部始终可见
- **账号系统**：注册 / 登录 / 学习进度追踪（可选，未登录也能用全部功能）

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

1. 首页点击「动物」进入，三种模式切换：
   - **浏览**：点方块 → 全屏弹窗（可前后翻页、点击图片缩放）
   - **卡片**：左右按钮翻页，点击图片放大（滚轮/双指缩放）
   - **练习**：看图片选正确词语，10 题后出成绩
2. 点击中文/英文/科普文字行即可播放对应语音
3. 右上角按钮切换主题：☀️深色 → 🌙浅色 → 🌓自动
4. 浏览模式「再来一次」重置已查看状态（未登录用 localStorage 记录）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 4.2.x, Python 3.12+ |
| 前端 | Alpine.js 3.14（本地托管）, 原生 CSS（CSS Variables） |
| 数据库 | SQLite |
| 图像处理 | Pillow, NumPy, OpenCV（headless） |
| 拼音排序 | pypinyin |

## Docker 部署

```bash
docker compose up -d
```

访问 `http://localhost:2511`。数据持久化到 `/mnt/usb2/Configs/learning-platform/data`。

## 项目结构

```
learning-platform/
├── apps/core/          # 核心应用（模型/视图/管理命令）
│   ├── image_utils.py  # 图片焦点检测 + emoji 取色
│   ├── models.py       # Category / Item / Progress / Quiz
│   └── management/commands/  # seed_data / detect_centers / ensure_media
├── apps/users/         # 用户模块（注册/登录/统计）
├── config/             # Django 配置
├── templates/          # HTML 模板（3 种模式 + 弹窗 + 登录）
├── static/             # CSS + JS
├── media/              # 图片与音频素材（已纳入 git）
└── requirements.txt
```

## 开发笔记

关键问题排查统一记录在 **DEV.md**。

## License

MIT
