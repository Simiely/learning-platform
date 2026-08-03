# AGENTS.md · 项目规则

> 给 AI / 未来的你：只记代码里看不出的关键信息。详细问题记录见 [DEV.md](DEV.md)（30+ 条一坑一篇）。

## 技术栈

- Django 6.0 + Python 3.13+ + SQLite；前端 Alpine.js 3.14.8（**本地托管，不用 CDN**）+ 原生 CSS（CSS Variables）
- 生产 gunicorn（仅 Docker）；Docker + GitHub Actions 自动构建推送 ghcr.io
- 拼音排序用 pypinyin；图像处理 Pillow / NumPy / OpenCV headless

## 关键坑

1. **iOS Safari 布局三坑**：① `100vh` 含地址栏高度且 bfcache 恢复用旧值 → 用 JS `--vh`（`window.innerHeight*0.01`）；② body 不要 `display:flex` + `min-height` 同时用（Safari 塌缩 bug）；③ `viewport-fit=cover` 必须配套 `env(safe-area-inset-*)` 避让刘海/状态栏
2. **关键 JS 库不用 CDN**——Safari Tracking Prevention 会拦截 CDN 域的 localStorage 访问导致脚本挂起，必须下载到 `static/` 本地托管
3. **iPad 判定用 `screen.width >= 768`**（物理宽），`window.innerWidth` 在 iPad 竖屏被夹到 ~375px 不可靠
4. **IIFE 前必须加分号**——上一语句缺 `;` 时 `} (function(){})()` 被解析成调用，TypeError 导致整段 script 后续代码全部终止（`(intermediate value)(...) is not a function`）
5. **Alpine 写入嵌套属性必须走 this**：`this.currentQuestion.image_position = x` ✅；`var q = this.currentQuestion; q.image_position = x` ❌ 不触发响应式
6. **数据表必须有稳定唯一键（code）**——`update_or_create(code=...)` 增量同步，从不删除用户数据（`seed_sync`，别用 `seed_data --force`）
7. **iOS 精确对齐别用 `<button>`**——Safari 渲染尺寸与 `<span>` 有底层偏差，用同元素类型
8. **图片焦点是手调值**——`image_position_checked=True` 防 `detect_centers --force` 覆盖；改焦点只改 `apps/core/data/` 后 `sync_positions`

## 约定

- 数据单一来源：`apps/core/data/`（CardItem dataclass + CATEGORIES），seed 命令都从它读取
- 全屏布局：`container` flex column + `height: calc(var(--vh,1vh)*100 - 52px)`，每层 `min-height:0` 防撑破
- 深色模式三态（dark/light/auto），颜色全走 CSS 变量不硬编码
- CSS 文件 `?v=YYYYMMDDx` 版本号防 Safari 强缓存；改 CSS 后必须更新版本号
- 新增条目：`audio_file` 基名全局唯一（跨分类不得重名）；模板 label 固定 `"emoji 文字"` 格式
- 提交前：`manage.py check` / `manage.py test apps.core` / `manage.py check_data`

## 常用命令

- 本地跑：`.venv/Scripts/python.exe manage.py runserver localhost:8000`
- 改数据后：`python manage.py seed_sync`（增量，安全）
- 数据校验：`python manage.py check_data`；部署见 [DEVELOPER.md](DEVELOPER.md)
