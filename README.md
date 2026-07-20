# Lets Learn —— 幼儿互动学习卡片

一个基于 Django + Alpine.js 的儿童学习闪卡平台，支持浏览、卡片、练习三种学习模式。

## 功能特性

- **浏览模式**：拼音首字母排序的动物卡片网格，emoji + 中英文名，点击弹出详情和发音
- **卡片模式**：全屏沉浸式翻转卡片，图片 contain 适配 + 自动播放中英文发音
- **练习模式**：看图选词语，答题反馈（正确高亮、错误标红、其余 20% 透明度）
- **三语发音**：中文、英文、科普语音，自动连播（中文 → 1秒后 → 英文）
- **智能配色**：
  - 浏览网格方块背景色 = emoji 平均色 + 70% 黑（PIL 渲染 emoji 取色）
  - 图片展示区背景色 = 图片平均色 + 60% 黑（NumPy + PIL 计算）
- **账号系统**：注册 / 登录 / 学习进度追踪

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 5.x, Python 3.13 |
| 前端 | Alpine.js, 原生 CSS (CSS Variables) |
| 数据库 | SQLite (开发), PostgreSQL (生产 Docker) |
| 图片处理 | Pillow, NumPy |
| 拼音排序 | pypinyin |
| 部署 | Docker + docker-compose |

## 快速启动

### 本地开发

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 初始化数据库
python manage.py migrate

# 3. 加载示例数据（动物卡片）
python manage.py seed_data

# 4. 启动开发服务器
python manage.py runserver
# 访问 http://localhost:8000
```

### Docker 部署

```bash
docker-compose up -d
```

### 创建管理员账号

```bash
python manage.py createsuperuser
# 访问 http://localhost:8000/admin/ 管理卡片内容
```

## 项目结构

```
learning-platform/
├── apps/
│   ├── core/          # 核心应用（Category、Item 模型）
│   │   ├── models.py       # 数据模型
│   │   ├── views.py        # 视图逻辑 + 图片取色
│   │   ├── admin.py        # 管理后台配置
│   │   └── management/commands/seed_data.py  # 种子数据
│   └── users/         # 用户应用（注册/登录）
├── config/            # Django 项目配置
├── templates/         # HTML 模板
│   ├── base.html           # 基础布局
│   ├── index.html          # 首页
│   ├── category_browse.html # 浏览模式
│   ├── category_cards.html  # 卡片模式
│   ├── category_quiz.html   # 练习模式
│   └── browse_popup.html   # 浏览弹窗
├── static/css/style.css # 全局样式
├── media/             # 用户上传媒体（gitignore）
├── Dockerfile
└── docker-compose.yml
```

## 管理后台

访问 `/admin/`，可以：
- 添加 / 编辑动物卡片（名称、英文名、emoji、图片、三种音频）
- 图片焦点 `bg_color` 字段自动计算（种子数据时），也可手动覆盖
- 管理分类（动物、水果、运动……）
- 查看学习进度和练习记录

## 添加新动物类别

1. 在管理后台创建 Category（如"水果"）
2. 准备素材放到 `media/` 目录：
   - `images/` — 图片
   - `audio/` — 中文语音
   - `audio_en/` — 英文语音
   - `audio_fact/` — 科普语音
3. 编辑 `seed_data.py` 添加新的 ANIMALS（或水果）列表
4. 运行 `python manage.py seed_data` 导入

## License

MIT
