# 开发笔记

记录开发过程中遇到的关键问题及解决方案，供后续开发参考。

## 1. 全屏布局 & flex 填满视口

**问题**：卡片模式和练习模式需要填满整个视口（除去导航栏），`height: 100vh` 不够精确。

**方案**：

```
container (display:flex; flex-direction:column; height:100vh)
  ├── nav (flex:none)
  └── main.container (flex:1; min-height:0; overflow:hidden)
      ├── .mode-bar (flex:none)
      └── .card-page / .quiz-page (flex:1; min-height:0)
```

关键规则：
- **整个 flex 链**从上到下每层都要设 `min-height:0`，否则内容会撑破容器
- `overflow:hidden` 在最外层防止溢出
- 需要自适应填满的元素用 `flex:1`，固定尺寸的元素用 `flex:none`

## 2. 练习模式 layout 跳动

**问题**：答题后 feedback 区出现"答对了/错了"文字和"下一题"按钮，导致整个页面 layout 跳动。

**根因**：用了 `<template x-if="answered">` 条件渲染——未答题时 DOM 不存在，答题后突然插入元素。

**解决**：
1. 全部改用 `x-show`（元素始终在 DOM 中，只是 `display:none`）
2. feedback 区写死 `height: 80px`（后压缩到 70px），无论内容显隐都占同样高度

## 3. 中文拼音排序

**问题**：浏览模式需要按中文名拼音首字母排序。

**方案**：使用 `pypinyin` 库：

```python
from pypinyin import pinyin, Style
items = sorted(items, key=lambda it: pinyin(it.name, style=Style.TONE3)[0][0])
```

注意：`Style.TONE3` 返回带数字声调的拼音（如 `chang2`），排序时声调会被忽略。

## 4. Emoji 取色 → 浏览页面方块背景

**问题**：浏览页面每个方块背景色应该基于该动物的 emoji 平均色，动态生成。

**方案**：用 PIL 渲染 emoji 到图片，采样非透明像素算平均色：

```python
font = ImageFont.truetype('C:/Windows/Fonts/seguiemj.ttf', 80)
img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.text((20, 20), emoji, font=font, embedded_color=True)
# 采样非透明像素 → 平均色 → 加 70% 黑
```

注意：
- Windows 上需要 Segoe UI Emoji 字体（`seguiemj.ttf`）
- `embedded_color=True` 确保彩色 emoji 正确渲染
- 结果缓存到 `_emoji_color._cache` 字典，避免重复计算

## 5. 图片平均色 → contain 模式背景

**问题**：图片使用 `object-fit:contain` 后会有留白区域，需要用图片本身的色调填充。

**方案**：用 PIL + NumPy 读取图片像素，计算非透明区域平均色，暗化 60%：

```python
def _image_bg_color(image_path, darken=0.6):
    img = Image.open(image_path).convert('RGBA')
    img.thumbnail((200, 200))  # 缩放加速
    arr = np.array(img)
    mask = arr[:,:,3] > 50  # 忽略透明像素
    r = int(arr[:,:,0][mask].mean())
    g = int(arr[:,:,1][mask].mean())
    b = int(arr[:,:,2][mask].mean())
    dark_r = int(r * (1 - darken))
    ...
```

存入 `Item.bg_color` 字段，前端 JS 动态设置容器 `backgroundColor`。

## 6. 音频后端数据传递

**问题**：中英科普三种音频需要正确传到前端。

**根因**：`items_json`（卡片模式用）和 `item_detail_api`（浏览弹窗用）是两处代码，容易漏改。

**解决**：
- 两处都用 `replace_all=true` 同步更新
- 配置 `MEDIA_URL = '/media/'` + `MEDIA_ROOT`
- 前端播放：`audio.src = '/media/' + it.audio_zh`

## 7. 闭包作用域 → onclick 失败

**问题**：卡片模式中 `onclick="playCardAudio('en')"` 无法播放。

**根因**：`items` 变量在 IIFE 闭包内，`onclick` 属性中的函数通过 `window` 调用，但引用的 `items` 闭包变量在某些情况下丢失。

**解决**：把 `items` 提升为 `window.cardItems` 全局变量。

## 8. Alpine.js 模板嵌套限制

**问题**：练习模式同时有 `x-if="state==='playing'"` 和 `x-if="quizType==='image_to_name'"`，嵌套 `<template x-if>` 容易混乱。

**注意**：
- Alpine.js 的 `x-if` 是真条件渲染（不存在的 DOM），`x-show` 只是 CSS 隐藏
- 两层 `x-if` 嵌套是支持的，但要注意变量作用域
- 内部模板引用 `currentQuestion.options` 是正确的（来自父级 x-data）

## 9. Django + 代理环境

**问题**：本地请求通过代理时需要特殊配置。

**方案**：settings.py 中不设代理相关配置，runserver 走 localhost 直连。curl 测试时加 `-k` 跳过 SSL 验证。

## 10. 种子数据中的文件写入（确定性，避免 404）

**问题**：seed_data 命令从 `media/audio/` 等目录复制文件到 Django 的 MEDIA_ROOT，并要求数据库字段名与磁盘文件名完全一致。

**根因 / 旧方案**：曾用 `item.audio.save(audio_file, ContentFile(f.read()))`。Django 的 `FileField.save` 在目标文件已存在时会追加随机 `_<suffix>`（见第 11 节），导致 DB 与磁盘不一致 → 404。

**新方案（`seed_data.py` 已落地）**：`seed_data` 改用 `_write_media_file(rel_path, bytes)` 直接以规范纯名覆盖写入（`rel_path` 统一为正斜杠），并在写入前清理同 stem 的随机后缀孤儿；同时在 `handle()` 开头调用 `_clean_orphan_suffixes()` 全局清扫历史孤儿。这样**随时重跑 seed_data 都安全**，且全新 clone + migrate + seed_data 必得一致文件名。

---

## 近期关键问题速查（2026-07-21）

下列问题根因隐蔽、易重复踩坑，遇到同类现象先查本节。

### 11. 音频 404：数据库文件名与磁盘文件名不一致（最高频）

**现象**：点击发声按钮无声音，控制台 `GET /media/audio/lion_v0KG1DD.mp3 404 (Not Found)`。

**根因**：磁盘文件是纯名 `media/audio/lion.mp3`（已提交进 git），但数据库 `audio` 字段存的是 `audio/lion_v0KG1DD.mp3`（带 Django 自动加的随机后缀）。二者对不上 → 404。

**为什么会不一致**：`seed_data` 用 `item.audio.save('lion.mp3', ContentFile(...))` 写入。Django 的 `FileField.save` 在**目标文件已存在**时，会经 `get_available_name` 自动追加 `_<7位随机>` 后缀避免覆盖。因此：
- 全新 clone + migrate + seed_data（此时 media 为空）→ 写 `lion.mp3`，DB 也 `lion.mp3` → 一致 ✅
- 在**已有 media 文件**的环境里再跑 seed_data → DB 变成 `lion_v0KG1DD.mp3`，但已提交的纯名 `lion.mp3` 仍在 → 不一致 ❌

**排查命令**（永远先看 DB 里实际存了什么名，别只看磁盘）：
```python
from apps.core.models import Item
i = Item.objects.get(name='狮子')
print(i.audio.name, '->', i.audio.url)   # DB 实际字段名 + 生成 URL
```
再 `ls media/audio | head` 对比磁盘文件名。注意：`curl` 直接测 `http://localhost:8000/media/audio/lion.mp3` 返回 200 会**暂时掩盖**问题——你测的是磁盘存在的纯名，不是 DB 请求的带后缀名。

**修复**：把 DB 字段名规范化回纯名（取 `_` 前英文名 base），先 `os.path.exists` 校验文件存在再 `setattr + save`。两个坑：
1. 用 `os.path.join` 在 Windows 会产生反斜杠 `audio\lion.mp3` → 必须再 `.replace('\\','/')`，否则 `.url` 把 `\` 编成 `%5C` 又 404。
2. 必须对所有 3 个字段（audio / audio_en / audio_fact）× 全部 Item 一起处理。

**已在代码层修复（2026-07-21）**：`seed_data.py` 改用 `_write_media_file()` 直接以规范纯名覆盖写入并清理随机后缀孤儿（见第 10 节），不再走 `FileField.save`。因此现在**随时重跑 seed_data 都安全**，无需先清空 media，全新 clone + migrate + seed_data 必得一致文件名。上面的「修复」步骤仅用于清理本机历史已损坏的数据库（本机已修复，可忽略）。

### 18. 全新部署 seed_data 崩溃：`bg_color` 字段已删除但仍被赋值

**现象**：全新 clone → `migrate` → `seed_data` 报 `ValueError: The following fields ... do not exist ... bg_color`。

**根因**：迁移 0007 / 0008 已移除 `Item.bg_color` 字段（前端也不再消费，属死代码），但 `seed_data` 仍在写 `item.bg_color = _image_bg_color(...)`。本地因数据库是从旧结构演化来的，不一定暴露；全新 clone 走最新迁移后字段不存在 → 崩溃。

**修复（2026-07-21）**：从 `seed_data` 删除 `bg_color` 赋值及相关 import。现在全新部署可正常 `seed_data`。

### 12. iPad「白色变黑色」= 智能反转，不是 CSS bug（血泪教训）

**现象**：白色描边 / 白字 / 白按钮，刷新后「先白后黑」，或一直黑；怎么改 CSS 都没用。

**真实根因**：iPad **设置 → 辅助功能 → 显示与文字大小 → 智能反转（Smart Invert）/ 经典反转**被打开。它会反转全局 UI 颜色但照片不动，于是所有白色 UI 被翻黑、照片保持原样，呈现「先白后黑 + 全白皆黑」。

**误诊历史（作废，勿再走）**：曾错误归因于 Safari `backdrop-filter` bug、圆形元素上 `border` / `inset box-shadow` 失效、WebKit #298341 `<button>` box-shadow 损坏，并因此用 `<div>` 替换 `<button>`、加 `::before` 伪元素描边等——**全是误诊，浪费大量迭代**。CSS 从一开始就是对的。

**正确排查顺序**：遇到「白变黑」先问用户 iPad 是否开了智能反转；关闭后即正常。不要先改 CSS。

### 13. iPad / Safari 的 CSS 缓存：必须带版本号

**现象**：改了 `static/css/style.css`，iPad 刷新后毫无变化，误以为改动没生效。

**根因**：Safari / iPad 对静态 CSS 缓存极顽固，只有 `?v=` 查询串变化才会重新拉取。

**规范**：每次改 `style.css`，把 `templates/base.html` 里的
`<link rel="stylesheet" href="{% static 'css/style.css' %}?v=YYYYMMDDX">`
版本号 +1（如 `?v=20260721aa`）。改完用 `curl -s "http://127.0.0.1:8000/static/css/style.css?v=..."` 验证服务器确实返回新版本与新规则，不要只信浏览器。

### 14. 本机运行 Django 的 venv 路径

**现象**：在 WorkBuddy Bash 里直接 `python manage.py runserver` 报缺少依赖 / ImportError。

**根因**：Bash 默认 `python` 指向 managed 3.13.12（无本项目依赖）；项目有专用 venv。

**正确命令（绝对路径）**：
```bash
"C:\Users\2504\Documents\260721\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8001
```
- 项目当前**唯一工作副本**为 `C:\Users\2504\Documents\260721`（旧的 `D:/workbuddy/2026-07-20-11-42-43/learning-platform` 已清空）。
- 启动前先杀掉占用 `:8001` 的旧进程。
- 服务器后台运行；改 CSS / 模板无需重启（Django 自动重载），改 Python 文件等自动重载或手动重启。
- 代理环境：git / curl 走 `127.0.0.1:7890`；`curl` 测试本地用 `-k` 跳过 SSL。

### 15. 深色 / 浅色模式：基于 CSS 变量

- 所有颜色走 `style.css` 的 `:root` 变量；深色模式 = `:root[data-theme="dark"]` 覆盖同一组变量（不新增 class）。
- `base.html` `<head>` 内联防闪烁脚本：读 `localStorage.theme` 提前设 `data-theme`，避免深色模式闪白。
- 切换按钮 `.theme-toggle` 调 `toggleTheme()`（切 `document.documentElement.dataset.theme` + 存 `localStorage` + 换图标）。
- 新增任何颜色**必须走变量**，不要硬编码，否则深色模式会漏色。

### 16. 浅色主色 + on-primary 对比度

- 主色 `#FF9292`（珊瑚粉）是浅色，白字压其上 WCAG AA 不达标。
- 约定：`--primary` 存主色；`--on-primary: #6e2a2a`（深玫瑰）专用于「主色底上的文字 / 图标」。
- 凡是 `background: var(--primary)` 的元素，其文字 / 图标用 `var(--on-primary)`。

### 17. 进场自动朗读被 iOS 拦截（非 bug）

**现象**：进卡片时控制台 `NotAllowedError: play() failed because the user didn't interact with the document first.`

**说明**：这是卡片进场时 `setTimeout(playCardAudio('zh'), 300)` 自动朗读，因处于 `setTimeout` 中、脱离用户手势上下文，被 iOS 自动播放策略拦截。`playCardAudio` 已有 `.catch` 静默处理，只影响进场自动读；**手动点击发声正常**（文件能加载）。iOS 无法绕过该限制，除非把朗读放进打开卡片的点击手势内。

### 19. 全新 clone `migrate`/`seed_data` 报 `ModuleNotFoundError: No module named 'cv2'`

**现象**：全新克隆 → `pip install -r requirements.txt` → `python manage.py migrate`（或 `seed_data`）报 `ModuleNotFoundError: No module named 'cv2'`。

**根因**：`apps/core/views.py` 用 OpenCV 做图片焦点 / 显著图检测（`cv2.imread`、`cv2.cvtColor`、`cv2.saliency.StaticSaliencyFineGrained_create()`、`cv2.Canny`）。但 `requirements.txt` 此前漏写 opencv 依赖——本地旧 venv 是手动 `pip install` 装上的，所以一直没暴露；全新环境只装 requirements.txt 就缺包。

**修复（2026-07-21，已推 `969ca6e`）**：`requirements.txt` 新增 `opencv-python-headless==5.0.0.93`。
- 用 **headless** 版（无 Qt / GTK 等 GUI 依赖），更轻、服务器环境无需显示后端。
- 锁版本 `5.0.0.93` 避免将来 ABI 漂移。

**教训**：任何被业务代码 `import` 的第三方包，必须进 `requirements.txt`；本地手动装过的包是隐形炸弹，换机即爆。CI / 全新 clone 是检验依赖完整性的唯一可靠方式。

### 20. 全新 clone `migrate` 报 `unable to open database file`（sqlite 父目录不存在）

**现象**：全新克隆 → `python manage.py migrate` 报 `sqlite3.OperationalError: unable to open database file`。

**根因**：`config/settings.py` 中 `DATABASES['default']['NAME'] = BASE_DIR / 'db' / 'db.sqlite3'`。`db/` 目录被 `.gitignore` 忽略、不会随仓库带来；而 Django 的 `migrate` 只负责建**文件**，不会自动建**父目录**。父目录不存在 → 写库失败。本地旧库是从更早的结构演化来的，`db/` 早已存在，所以一直没暴露。

**修复（2026-07-21，已推 `969ca6e`）**：在 `settings.py` 定义 `DATABASES` 之后、迁移前，确保父目录存在：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}
os.makedirs(os.path.dirname(str(DATABASES['default']['NAME'])), exist_ok=True)
```
`os.makedirs(..., exist_ok=True)` 幂等，重复调用安全。

**教训**：凡 DB 路径指向一个**不在仓库内、需要本地生成**的目录，务必在 settings 里 `makedirs` 兜底，不要假设目录已存在。

### 21. 工作副本已迁移到新文件夹（2026-07-21）

**背景**：原工作副本 `D:/workbuddy/2026-07-20-11-42-43/learning-platform` 已清空；当前**唯一工作副本**为 `C:\Users\2504\Documents\260721`（从 GitHub 全新克隆，`master` 已含全部修复）。

**约定**：
- venv 在本文件夹内：`C:\Users\2504\Documents\260721\venv\Scripts\python.exe`（Python 3.13.12）。
- 本机运行端口用 `:8001`（原 `:8000` 留给旧副本，现已弃用）。
- 所有改动先在本文件夹 commit，再 `git push origin master`（远程 URL 已带 PAT，走 `127.0.0.1:7890` 代理）。
