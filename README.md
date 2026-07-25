# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django + Alpine.js** 的幼儿识字/认知闪卡平台，支持 **浏览、卡片、练习** 三种学习模式，专为触屏（iPad / iPhone）设计，无需登录即可使用。支持 41 种动物中英文对照学习，配三语自动发音。

## 功能特性

- **浏览模式**：拼音排序的卡片网格，点击弹出全屏详情（支持图片缩放 + 前后翻页）+ 自动发音
- **卡片模式**：全屏沉浸式翻卡，随机起始 + 拼音排序，图片缩放+拖拽（滚轮/双指缩放，鼠标/单指平移）
- **练习模式**：看图选词，即时反馈，10 题一组不重复。答对撒花 + 音效，答错柔和提示 + 显示正确答案
- **三语发音**：中文名称 / 英文名称 / 科普知识（中文），自动连播，每只动物独立音频
- **智能配色**：浏览方块背景基于 emoji 平均色动态生成（Pillow + NumPy）
- **三态主题**：深色 → 浅色 → 自动（跟随系统），偏好记忆到 localStorage
- **图片焦点**：每张图片手动校准视觉中心，iPhone / iPad 竖屏 / iPad 横屏三套独立焦点，动物脸部始终可见
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
5. 修改动物数据（焦点、科普等）：编辑 `seed_data.py` → `python manage.py seed_sync`（增量更新，不删数据）

## 部署 & 更新

```bash
# 首次部署（需 .env 中设置 DJANGO_SECRET_KEY）
docker compose up -d

# 更新已有部署
docker compose pull && docker compose up -d
# 容器自动 migrate + seed_sync，不丢数据
```

> **首次部署时**，数据库为空，容器自动执行 seed_data 填充 41 只动物数据。
> **更新部署时**，不需要删数据库。seed_sync 只在发现新动物时追加。

| 层级 | 技术 |
|------|------|
| 后端 | Django 4.2.x, Python 3.12+ |
| 前端 | Alpine.js 3.14（本地托管，不用 CDN）, 原生 CSS（CSS Variables） |
| 数据库 | SQLite（单文件，Docker 卷持久化） |
| 音频生成 | edge-tts（Microsoft 神经网络语音，中文 Xiaoxiao / 英文 Jenny） |
| 图像处理 | Pillow, NumPy, OpenCV（headless） |
| 拼音排序 | pypinyin |
| 容器化 | Docker + GitHub Actions（自动构建推送 ghcr.io） |

## Docker 部署

支持一键 Docker 部署，镜像通过 GitHub Actions 自动构建推送。

```bash
docker compose up -d
```

访问 `http://服务器IP:2511`。数据持久化到 `./data/`（db + media），容器重建不丢数据。

**更新部署**：`docker compose pull && docker compose up -d`

> `.env` 文件中需设置 `DJANGO_SECRET_KEY`。

## 项目结构

```
learning-platform/
├── apps/core/                  # 核心应用
│   ├── models.py               # Category, Item, LearningProgress, QuizAttempt
│   ├── views.py                # 视图 + API（含三套焦点返回）
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
│   ├── category_cards.html     # 卡片模式（含 zoom + 拖拽 + iPad 检测）
│   ├── category_quiz.html      # 练习模式（含 confetti + audio）
│   └── browse_popup.html       # 浏览弹窗
├── static/
│   ├── css/style.css           # 全局样式（CSS Variables，深/浅两套 token）
│   └── js/
│       ├── alpine.min.js       # Alpine.js 本地托管（不用 CDN！）
│       ├── theme.js            # 三态主题切换
│       ├── popup.js            # 浏览弹窗逻辑
├── media/                      # 图片 + 音频素材（41 只动物，进 git）
├── ANIMALS.md                  # 动物数据主清单（含三套焦点）
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
- iPhone / iPad 竖屏 / iPad 横屏三套独立图片视觉焦点

---

## AI 开发注意事项

> 以下规范写给 AI 助手（以及未来的你），确保修改项目时不出错。

### 数据修改铁律

**所有动物数据只能通过 `seed_data.py` 修改，禁止直接操作数据库。**

```
apps/core/management/commands/seed_data.py  ← 唯一的数据源
```

修改流程：

```bash
# 1. 编辑 seed_data.py（改焦点、科普、新增动物等）
# 2. 同步到数据库
python manage.py seed_sync
# 3. 重启服务（Django runserver 自动重载，无需手动）
```

- `seed_sync` 用 `code` 字段做唯一键匹配（如 `lion_2026072302`），改名/换 emoji 不影响匹配
- 永远不会删除已有数据，只会增量更新或原地修改
- **不能用 `seed_data --force`**：会删库重建，Docker 环境会丢用户进度

### seed_data.py 元组结构（10 个字段）

```python
('中文名', 'code', '英文名', 'emoji', '图片文件', '音频文件',
 '科普知识',
 'iphone焦点',      # iPhone 竖屏，如 '50% 50%'
 'ipad竖焦点',      # iPad 竖屏，如 '50% 40%'
 'ipad横焦点'),     # iPad 横屏，如 '50% 30%'
```

- code 格式：`english_lower_YYYYMMDDNN`（如 `polar_bear_2026072401`），全局唯一
- 所有焦点格式：`'X% Y%'`，X=水平（左0%→右100%），Y=垂直（上0%→下100%）
- **元组解包顺序绝对不能错**：第 8、9、10 个分别是 iPhone / iPad 竖 / iPad 横

### 前端焦点检测（三页面实现不同）

| 页面 | 检测方式 | 文件 |
|------|---------|------|
| 卡片 | 全局函数 `getImagePos(it)` 按 `screen.width>=768` 判断 | `category_cards.html` |
| 练习 | Alpine `nextQuestion()` 中 `this.currentQuestion.image_position` 替换 | `category_quiz.html` |
| 浏览 | popup 加载时 `screen.width>=768` → 选对应字段 | `browse_popup.html` |

iPad 检测用 `screen.width`（物理像素），不用 `window.innerWidth`（不可靠）。

### JS 编码规范

- **每个函数声明末尾加分号**：`function foo() { ... };` ← 必须
- IIFE 前确保上一语句已终止（`;` 不能省），否则报 `(intermediate value)(...) is not a function`
- Alpine 中修改嵌套对象属性必须走 `this.xxx.yyy` 路径（Proxy 响应式），不能通过局部变量
- Alpine.js 本地托管在 `static/js/alpine.min.js`，**不要用 CDN**（Safari 追踪防护会拦截）

### Safari 特殊处理

- `100vh` 在 iOS Safari 含地址栏高度，卡片/练习模式直接 `height: calc(100vh - 52px)` 适配
- **body 不要同时设 `display: flex` + `min-height`**（Safari bug：子元素不会扩展）
- `cursor: grab/grabbing` 需要 `-webkit-` 前缀自动处理
- 练习模式 CSS 布局链不能破坏：`container-card(固定高度) → quiz-body(flex:1) → quiz-round(flex:1,min-height:0)`

### 文件编码

- 所有 Python 模板和 HTML 用 UTF-8
- Windows 下 `.bat` / `.ps1` 用纯 ASCII（避免 GBK 乱码）

### Docker 构建

- 推送到 `master` 分支自动触发 GitHub Actions → 构建镜像 → 推送到 ghcr.io
- `cancel-in-progress: true`，同一分支多次推送只保留最后一次构建
- 容器入口 `/docker-entrypoint.sh` 自动执行 migrate + seed_sync

### 常见错误速查

| 现象 | 根因 | 解决 |
|------|------|------|
| 卡片全崩，只显示 emoji | JS 缺少分号，后续代码不执行 | 查 Console 红色报错 |
| 图片焦点调整不生效 | 前端没接 iPad 字段 | 确认三页面都接入检测 |
| 练习容器不填满 | body flex + min-height bug | 回退 body CSS |
| Docker 部署后数据异常 | 反了元组顺序 | 重新从 seed_data.py 校验 |
| 音频播放 404 | 磁盘文件名与 DB 不一致 | seed_data 用 `_write_media_file()` 覆写 |

## License

MIT
