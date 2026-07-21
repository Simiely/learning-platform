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

## 快速开始

```bash
# 1. 虚拟环境与依赖（注意：numpy / pypinyin 必需，已写入 requirements.txt）
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 初始化数据库并加载 21 个动物示例数据
python manage.py migrate
python manage.py seed_data

# 3. 启动开发服务器
python manage.py runserver        # 访问 http://localhost:8000
```

创建管理员账号（用于后台管理卡片内容）：

```bash
python manage.py createsuperuser  # 访问 http://localhost:8000/admin/
```

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
