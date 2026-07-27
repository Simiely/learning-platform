# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django + Alpine.js** 的幼儿识字/认知闪卡平台，支持 **浏览、卡片、练习** 三种学习模式，专为触屏（iPad / iPhone）设计，无需登录即可使用。内置 41 种动物的中英文对照学习，配三语自动发音。

## 功能特性

- **浏览模式**：拼音排序的卡片网格，点击弹出全屏详情（支持图片缩放 + 前后翻页）+ 自动发音
- **卡片模式**：全屏沉浸式翻卡，随机起始 + 拼音排序，图片缩放 + 拖拽（滚轮/双指缩放，鼠标/单指平移）
- **练习模式**：看图选词（image-to-name），即时反馈，10 题一组不重复。答对撒花 + 音效，答错柔和提示 + 显示正确答案
- **三语发音**：中文名称 / 英文名称 / 科普知识（中文），自动连播，每只动物独立音频
- **智能配色**：浏览方块背景基于 emoji 平均色在渲染时动态生成（Pillow）
- **三态主题**：深色 → 浅色 → 自动（跟随系统），偏好记忆到 localStorage
- **图片焦点**：每张图片支持 iPhone / iPad 竖屏 / iPad 横屏三套独立视觉焦点（手动校准为主，OpenCV 自动检测可选），动物脸部始终可见
- **账号系统**：注册 / 登录 / 学习进度追踪（可选），未登录也能用全部功能

## 快速开始（本地开发）

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

> 本地开发用 `seed_data` 做一次性全量写入（会清空后重建动物数据）；Docker 部署走 `seed_sync` 增量同步，二者不要混用。

## 使用方法

1. 首页点击「动物」进入，三种模式切换（页面顶部模式栏）：
   - **浏览** `/category/animals/`：方块网格 → 点击进入全屏弹窗（可前后翻页、点图缩放、自动发音）
   - **卡片** `/category/animals/cards/`：左右按钮翻页，随机起始，进场自动播放中英文
   - **练习** `/category/animals/quiz/`：看图选词，10 题一组，答对有礼花特效
2. 点击中文 / 英文 / 科普文字行即可播放对应语音
3. 右上角按钮切换主题：深色 → 浅色 → 跟随系统
4. 浏览模式「再来一次」重置已查看状态（未登录用 localStorage 记录）
5. 修改动物数据（焦点、科普等）：编辑 `seed_data.py` → `python manage.py seed_sync`（增量更新，不删数据）

## 部署（Docker）

镜像由 GitHub Actions 在推送 `master` 时自动构建并推送到 `ghcr.io/simiely/learning-platform:latest`。

### ⚠️ 部署前必读

1. **数据卷路径是硬编码的，必须先改！**
   仓库自带的 `docker-compose.yml` 把数据卷挂到了作者自己的 NAS 路径：
   ```yaml
   volumes:
     - /mnt/usb2/Configs/learning-platform/data/db:/app/db
     - /mnt/usb2/Configs/learning-platform/data/media:/app/media
   ```
   在你自己的机器上部署前，请改成你主机上的路径（推荐相对路径 `./data`）：
   ```yaml
   volumes:
     - ./data/db:/app/db
     - ./data/media:/app/media
   ```
   否则数据会写到不存在的 `/mnt/usb2/...` 目录（容器以 `root` 运行会自行创建该目录，迁移/重启后容易丢失或错乱）。

2. **默认管理员账号**
   首次启动，容器会用环境变量 `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD`（默认 `admin` / `admin1234`）自动创建一个超级管理员。生产环境务必在 `.env` 中改掉默认密码，或在启动后用 `python manage.py changepassword admin` 修改。

3. **SECRET_KEY**
   仅当 `DJANGO_DEBUG=false`（生产）时才**必须**设置 `DJANGO_SECRET_KEY`。
   默认 `docker-compose.yml` 里 `DJANGO_DEBUG` 为 `true`，会用随机/开发密钥，可直接 `up`。
   生产部署请设 `DJANGO_DEBUG=false` 并配置 `DJANGO_SECRET_KEY` 与反向代理（DEBUG 关闭后 Django 不再托管 `/static/` 与 `/media/`）。

### 首次部署

```bash
docker compose up -d
```

容器启动（`docker-entrypoint.sh`）会自动依次执行：

1. `collectstatic` 收集静态文件
2. `migrate` 迁移数据库
3. 从镜像内置的 `media-bundled` 副本 `rsync` 媒体到数据卷（仅传变化文件）
4. `seed_sync` 写入 41 只动物（增量更新，不会删除已有数据）
5. 创建默认管理员（如已存在则跳过）
6. 用 gunicorn 在容器内的 `0.0.0.0:8000` 启动

- 访问 `http://服务器IP:2511`（宿主机 2511 映射到容器 8000）。
- 数据持久化在上面的数据卷里，容器重建不丢数据。

### 更新部署

```bash
docker compose pull && docker compose up -d
```

`docker-compose.yml` 已配置 `pull_policy: always`，Dpanel 点「更新」等价于 restart + pull。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 4.2.20, Python 3.12+ |
| 前端 | Alpine.js 3.14.8（本地托管，不用 CDN）, 原生 CSS（CSS Variables） |
| 数据库 | SQLite（单文件，Docker 卷持久化） |
| 生产服务器 | gunicorn（仅 Docker 内使用） |
| 音频素材 | 预生成并随仓库提交（中文 / 英文 / 科普 三套 mp3）；`edge-tts` 仅用于离线重新生成音频，不是运行时依赖，也未列入 `requirements.txt` |
| 图像处理 | Pillow, NumPy, OpenCV（headless） |
| 拼音排序 | pypinyin |
| 容器化 | Docker + GitHub Actions（自动构建推送 ghcr.io） |

## 项目结构

```
learning-platform/
├── apps/core/                  # 核心应用
│   ├── models.py               # Category, Item, LearningProgress, QuizAttempt
│   ├── views.py                # 视图 + API（含三套焦点返回）
│   ├── image_utils.py          # emoji 取色 + 图片焦点检测
│   └── management/commands/
│       ├── seed_data.py        # 种子数据（41 只动物，含三套焦点）
│       ├── seed_sync.py        # 增量同步到数据库（更新部署安全）
│       ├── sync_positions.py   # 同步图片焦点到数据库
│       └── detect_centers.py   # OpenCV 自动检测焦点（不要用 --force）
├── apps/users/                 # 用户模块
├── config/                     # Django 配置
├── templates/                  # HTML 模板
│   ├── base.html               # 公共布局（全局 CSS/JS 加载）
│   ├── index.html              # 首页（板块卡片）
│   ├── category_browse.html    # 浏览模式（Emoji 方块网格）
│   ├── category_cards.html     # 卡片模式（翻卡 + 缩放拖拽）
│   ├── category_quiz.html      # 练习模式（看图选词 + 礼花）
│   ├── browse_popup.html       # 浏览弹窗（图片缩放 + 发音）
│   ├── login.html / register.html / profile.html
├── static/
│   ├── css/                    # 模块化 CSS（按页面拆分）
│   │   ├── theme.css           # 设计令牌 + 深色/浅色/自动主题
│   │   ├── layout.css          # 导航栏 + 模式栏 + 发音按钮
│   │   ├── buttons.css         # 按钮系统
│   │   ├── index.css           # 首页板块卡片
│   │   ├── browse.css          # 浏览方块网格
│   │   ├── popup.css           # 弹窗遮罩 + 卡片布局
│   │   ├── cards.css           # 卡片全屏模式
│   │   ├── quiz.css            # 练习模式
│   │   ├── auth.css            # 登录/注册
│   │   ├── profile.css         # 统计页
│   │   ├── zoom.css            # 全屏图片缩放遮罩
│   │   └── utils.css           # 工具类
│   └── js/
│       ├── alpine.min.js       # Alpine.js 本地托管（不用 CDN！）
│       ├── utils.js            # 工具函数
│       ├── ipad-detect.js      # iPad 焦点检测 + 卡片焦点上偏
│       ├── audio-player.js     # 统一音频播放（基于时长自动连播）
│       ├── image-zoom.js       # 图片缩放/拖拽（滚轮+双指+拖拽）
│       └── confetti.js         # 礼花特效 + Web Audio 音效
├── media/                      # 图片 + 音频素材（41 只动物，进 git）
├── ANIMALS.md                  # 动物数据主清单（含三套焦点）
├── DEV.md                      # 开发笔记（详细踩坑记录）
├── Dockerfile
├── docker-entrypoint.sh
├── docker-compose.yml          # ⚠️ 数据卷路径为作者 NAS，部署前需改
└── requirements.txt
```

> 注：`static/css/style.css` 是模块化重构前的旧版单文件样式，**未在任何模板中加载**（全局样式现由 `theme/layout/buttons/utils.css` 承载，各页面样式拆分到对应文件），仅作参考保留。

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
 'image_position',          # iPhone / 通用焦点，如 '13% 47%'
 'image_position_ipad_portrait',   # iPad 竖屏，如 '23% 37%'
 'image_position_ipad_landscape'), # iPad 横屏，如 '23% 47%'
```

- code 格式：`english_lower_YYYYMMDDNN`（如 `polar_bear_2026072401`），全局唯一
- 所有焦点格式：`'X% Y%'`，X=水平（左0%→右100%），Y=垂直（上0%→下100%）
- **元组解包顺序绝对不能错**：第 8、9、10 个分别是 iPhone（通用）/ iPad 竖 / iPad 横

### 前端架构（模块化）

项目经过模块化重构，前端资源按功能拆分：

**CSS 模块加载规则**：
| 文件 | 加载范围 | 内容 |
|------|---------|------|
| `theme.css` | 全局 | 设计令牌、深色/浅色/自动主题、reset |
| `layout.css` | 全局 | 导航栏、模式栏、发音按钮样式 |
| `buttons.css` | 全局 | 按钮系统 |
| `utils.css` | 全局 | 工具类 |
| `index.css` | 首页 | 板块卡片网格 |
| `browse.css` | 浏览页 | Emoji 方块网格 |
| `popup.css` | 浏览页 | 弹窗遮罩 + 卡片布局 |
| `cards.css` | 卡片页 | 全屏翻卡 |
| `quiz.css` | 练习页 | 答题界面 |
| `auth.css` | 登录/注册 | 表单样式 |
| `profile.css` | 统计页 | 统计瓷砖 |
| `zoom.css` | 卡片+浏览 | 全屏图片缩放遮罩 |

全局样式在 `base.html` 的 `<head>` 中通过 `{% block extra_css %}` 加载；页面专属 CSS 在各模板的 `extra_css` 块中加载。

**JS 共享模块**：
| 模块 | 导出 | 用途 |
|------|------|------|
| `ipad-detect.js` | `iPadDetect.getImagePos()`, `.centerPos()` | iPad 焦点检测 + 卡片上偏 |
| `audio-player.js` | `AudioPlayer(el)` → `play()`, `stop()`, `playSequence()` | 基于音频时长的中→英自动连播 |
| `image-zoom.js` | `ImageZoom.init()` | 图片缩放/拖拽（滚轮+双指+拖拽+双击重置） |
| `confetti.js` | `Confetti.launch()`, `.playCorrectSound()`, `.playWrongSound()` | 礼花 + Web Audio 音效 |

**关键设计规则**：
- `ipad-detect.js` 和 `utils.js` 在 `<head>` 中同步加载（无 `defer`），确保页面内联脚本执行前可用
- **CSS 版本号**：修改任何 CSS 后，更新所有模板中的 `?v=YYYYMMDDx` 版本号（当前为 `?v=20260726b`），否则 Safari 强缓存不更新

### 前端焦点检测

现在统一使用 `iPadDetect.getImagePos(item)` 模块（`ipad-detect.js`）：

```javascript
// 卡片模式：需要向上偏移（动物脸部通常在上部）
img.style.objectPosition = iPadDetect.centerPos(iPadDetect.getImagePos(it));

// 浏览/练习模式：直接用原始焦点
img.style.objectPosition = iPadDetect.getImagePos(data);
```

iPad 检测用 `screen.width >= 768`（物理像素），不用 `window.innerWidth`（Safari 竖屏会缩放）。

### JS 编码规范

- **每个函数声明末尾加分号**：`function foo() { ... };` ← 必须
- IIFE 前确保上一语句已终止（`;` 不能省），否则报 `(intermediate value)(...) is not a function`
- Alpine 中修改嵌套对象属性必须走 `this.xxx.yyy` 路径（Proxy 响应式），不能通过局部变量
- Alpine.js 本地托管在 `static/js/alpine.min.js`，**不要用 CDN**（Safari 追踪防护会拦截）

### Safari 特殊处理

- **状态栏/刘海适配**：`viewport-fit=cover` + `env(safe-area-inset-top)`，导航栏和弹窗按钮自动避让 iPhone 刘海/灵动岛和 iPad 状态栏
- **100vh 地址栏 Bug**：iOS Safari 的 `100vh` 含地址栏高度，卡片/练习模式用 JS 计算的 `--vh` 自定义属性（`window.innerHeight`）替代原生 `100vh`，配合 `viewport-fit=cover` 避免溢出
- **body 不要同时设 `display: flex` + `min-height`**（Safari bug：子元素不会扩展到 min-height）
- `cursor: grab/grabbing` 需要 `-webkit-` 前缀自动处理
- 练习模式 CSS 布局链不能破坏：`container-card(固定高度) → quiz-body(flex:1) → quiz-round(flex:1,min-height:0)`

### 文件编码

- 所有 Python 模板和 HTML 用 UTF-8
- Windows 下 `.bat` / `.ps1` 用纯 ASCII（避免 GBK 乱码）

### Docker 构建

- 推送到 `master` 分支自动触发 GitHub Actions → 构建镜像 → 推送到 ghcr.io
- `cancel-in-progress: true`，同一分支多次推送只保留最后一次构建
- 容器入口 `/docker-entrypoint.sh` 自动执行 migrate + seed_sync + 媒体同步 + 创建默认管理员
- 镜像内置 `/app/media-bundled` 副本，启动时用 `rsync` 同步到数据卷（仅传变化文件）

### 常见错误速查

| 现象 | 根因 | 解决 |
|------|------|------|
| 卡片崩，只显示 emoji | JS 缺少分号 或 `iPadDetect` 未加载 | 查 Console；确认 ipad-detect.js 在 head 同步加载 |
| 图片焦点不生效 | 前端没接 iPad 字段 | 使用 `iPadDetect.getImagePos()` |
| 发音按钮样式丢失 | 页面没加载对应 CSS 模块 | 确认 `.ph-*` 样式在 `layout.css`（全局加载） |
| 翻卡时英文覆盖中文 | `playSequence` 未取消旧序列 | 检查 `audio-player.js` 的 `sequenceId` 机制 |
| 首次加载不发音 | 浏览器 autoplay 拦截 | 已加解锁逻辑，用户点屏幕即可 |
| Docker 部署后异常 | 元组顺序错 | 从 seed_data.py 校验 |
| 音频 404 | 磁盘文件名与 DB 不一致 | seed_data 用 `_write_media_file()` 覆写 |
| CSS 改了不生效 | Safari 强缓存 | 更新所有模板的 `?v=` 版本号 |
| 练习模式容器塌缩 | quiz.css 缺少全视口样式 | 确认 `.container-quiz` 含 `height: calc(var(--vh)*100-52px)` |
| 练习答题后音频混乱 | `playQuizAudio` 引用动态属性被覆盖 | 用闭包冻结题目快照 + `_quizSeqId` 防护 |

## License

MIT
