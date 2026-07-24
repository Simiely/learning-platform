# 项目说明 / Project Context

> 写给下一个接手这个项目的 AI（或你自己）。读完这个文件，你应该能理解项目结构、关键决策、以及怎么做不踩坑。

## 项目概述

**Lets Learn** — 幼儿识字/认知闪卡平台。

### 前置清单

更新项目内容（增减动物、修改科普、调整图片焦点）的第一步是编辑 **`ANIMALS.md`**。这是所有动物数据的主数据源，包含：

- 41 只已上线动物（全部图片焦点已手动校准 ✅，含 iPhone / iPad 双套焦点）
- 中英文名、Emoji、图片/音频文件名、科普知识、图片焦点

修改清单后，再同步更新 `seed_data.py` 里的 `ANIMALS` 表格，重新部署即可生效。Django 后端 + Alpine.js 前端，专为 iPad / iPhone 触屏设计。

仓库：`github.com/Simiely/learning-platform`
本地工作目录：`D:\workbuddy\2026-07-23-09-03-34\learning-platform`

## 三种模式

| 模式 | 路由 | 说明 |
|------|------|------|
| 浏览 | `/category/<slug>/` | Emoji 方块网格，点击弹出全屏详情（可前后翻页、点图缩放） |
| 卡片 | `/category/<slug>/cards/` | 沉浸式翻卡，随机起始，进场自动发音 |
| 练习 | `/category/<slug>/quiz/` | 看图选词，10 题一组，答对撒花，答错显示正确答案 |

## 技术栈

- 后端：Django 4.2, Python 3.12+
- 前端：Alpine.js 3.14（本地 `static/js/alpine.min.js`，不用 CDN）
- 数据库：SQLite（`db/db.sqlite3`，不进 git）
- 图像：Pillow, NumPy, OpenCV headless
- 拼音：pypinyin
- 部署：GitHub Actions → Docker → ghcr.io → docker compose

## 项目结构

```
learning-platform/
├── apps/core/              # 核心应用
│   ├── models.py           # Category, Item (含 image_position_ipad), LearningProgress, QuizAttempt
│   ├── views.py            # 所有视图 + API（返回 iPhone/iPad 双焦点）
│   └── management/commands/
│       ├── seed_data.py    # 种子数据（41只动物），含 iPhone/iPad 双套焦点
│       ├── sync_positions.py  # 每次部署同步图片焦点到数据库
│       ├── detect_centers.py  # OpenCV 自动检测焦点（不要用 --force）
│       └── ensure_media.py    # （已废弃，媒体现在从镜像bundle同步）
├── apps/users/             # 用户模块
├── config/                 # Django 配置
├── templates/              # HTML 模板
│   ├── base.html           # 公共布局
│   ├── category_browse.html # 浏览模式
│   ├── category_cards.html  # 卡片模式（含 card-zoom.js）
│   ├── category_quiz.html   # 练习模式（含 confetti + audio）
│   ├── browse_popup.html    # 浏览弹窗（共用）
│   └── ...
├── static/
│   ├── css/style.css       # 全局样式（CSS Variables，深色/浅色两个 token 集）
│   ├── js/
│   │   ├── alpine.min.js   # Alpine.js 本地托管（不用 CDN！）
│   │   ├── theme.js        # 三态主题切换
│   │   ├── popup.js        # 浏览弹窗逻辑
│   │   └── card-zoom.js    # 卡片图片缩放
│   └── ...
├── media/                  # 图片 + 音频素材（进 git）
├── Dockerfile
├── docker-entrypoint.sh    # 容器启动脚本
├── docker-compose.yml
├── .github/workflows/build.yml  # CI：test → build Docker image & push
├── README.md               # 用户文档
├── DEV.md                  # 开发笔记（踩坑记录）
└── PROJECT.md              # 这个文件
```

## 关键设计决策

### 为什么 Alpine.js 要本地托管

Safari 智能追踪防护会阻止 CDN 的 Alpine.js 访问 localStorage，导致卡顿。`static/js/alpine.min.js` 本地托管，同域不触发防护。

### 为什么不用 `<button>` 做"再来一次"

iOS Safari 对 `<button>` 元素有渲染偏差，即使 CSS 完全一致，尺寸也和 `<span>` 不一样。用 `<span class="mode-badge mode-badge-reset">` 复用 badge 的盒模型，只覆写颜色。

### 图片焦点（image_position）

- `seed_data.py` 中 ANIMALS 表格的最后一列是手动校准的 `image_position`（如 `"23% 47%"`）
- 现在支持**iPhone / iPad 两套独立焦点**，`image_position`（iPhone）和 `image_position_ipad`（iPad）
- `Item.image_position_checked = True` 标记手调值，`detect_centers` 不会覆盖
- `sync_positions` 命令每次容器启动执行，从 seed_data 同步到数据库
- 卡片模式：`centerPos()` 对纵向做 ×0.65 上偏补偿（动物脸部通常在看图片上半部分）

### Docker 媒体同步

- 镜像自带 `/app/media-bundled`（.dockerignore 不排除 media/）
- 每次启动 `rsync -ac` 从 bundled 同步到卷（checksum 比较，只传变化文件）
- `sync_positions` 同步图片焦点
- 数据（db + media）在卷 `/mnt/usb2/Configs/learning-platform/data`

## 常见坑

### 1. 别用 `detect_centers --force`
会覆盖手动校准的 `image_position`。如果需要调整焦点，直接改 `seed_data.py` 里的值。

### 2. CSS 改完 iPad 不生效
Safari 强缓存。每次改 `style.css` 必须更新 `base.html` 里的 `?v=` 版本号。

### 3. 练习模式按钮溢出
`quiz-feedback` 高度必须 ≥ 内容需求。内容 = padding+文字区+按钮边距+按钮高度。布局链 `container-card(overflow:hidden) → quiz-round(flex:1,min-height:0)`。调整后验证 `∑(flex:none) ≤ height(container-card)`。

### 4. iPad 白变黑
不是 CSS bug，是 iPad 辅助功能里的「智能反转」打开了。不要改代码。

### 5. 本机运行
```bash
.venv/Scripts/python manage.py runserver localhost:8000
```
网络走代理 `127.0.0.1:7890`，git 有时需要 `GIT_SSL_NO_VERIFY=1 git -c http.proxy=http://127.0.0.1:7890 push`。

### 6. 部署更新
```bash
docker compose pull && docker compose up -d
```
不要用 Dpanel 的更新按钮（可能不 pull 新镜像）。

## 部署地址

- 本地：`http://localhost:8000`
- Docker：`http://服务器IP:2511`
- Docker 数据：`/mnt/usb2/Configs/learning-platform/data`

## 最后

DEV.md 里有更详细的踩坑记录。改之前先搜一下有没有前人趟过的雷。
