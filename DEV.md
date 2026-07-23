# 开发笔记

记录开发过程中遇到的关键问题及解决方案。

---

## 布局 & CSS

### 全屏布局

卡片和练习模式填满视口：`container` flex column + `height: calc(100vh - 52px)`，每层 `min-height: 0` 防止撑破。

### 图片焦点校准

- `image_utils.py` 用 OpenCV saliency 检测图片视觉重心，但检测的是整只动物的几何中心，不是脸部
- 所有 `image_position` 值已在 `seed_data.py` 的 ANIMALS 表格中手动校准，标记 `image_position_checked=True`
- **不要用 `detect_centers --force` 覆盖手调值**
- 卡片模板中 `centerPos()` 对纵向做 ×0.65 上偏补偿
- 修改焦点：改 `seed_data.py` 中对应动物的 `'XX% YY%'`，然后 `seed_data --force`

### 模式栏按钮对齐

**问题**：浏览/卡片/练习三个页面切换时，模式栏按钮位置跳动。

**根因**：
1. 浏览页多了「再来一次」按钮，总宽度 360px，iPhone 375px 下 `flex-wrap: wrap` 导致折行
2. 浏览页容器 `padding-top: 28px`，卡片/练习页 `container-card` 把容器 padding 归零 + mode-bar `padding-top: 16px`，顶部间距不一致

**修复**：
- 去掉 `.mode-bar` 的 `flex-wrap: wrap`
- `.container` 顶部 padding 从 28px 改为 16px，与卡片/练习的 mode-bar 顶部对齐

### `<button>` vs `<span>` 在 iOS Safari 的渲染差异（血泪教训）

**问题**：「再来一次」按钮的尺寸反复调整仍无法与 badge 对齐，iPhone 上明显偏大。

**排查过程**：逐条对比 CSS，font-size、padding、min-height、line-height、border、box-sizing 完全一致，但 `<button>` 仍比 `<span>` 宽/高几 px。

**根因**：iOS Safari 对 `<button>` 元素有底层渲染偏差，即使设置 `appearance: none`、`box-sizing: border-box`，实际渲染尺寸仍与 `<span>` 有细微差异。

**修复**：把「再来一次」从 `<button class="reset-btn">` 改为 `<span class="mode-badge mode-badge-reset">`，复用 badge 的盒模型，只覆写颜色。自此 iPad 和 iPhone 尺寸完美一致。

**教训**：需要跟相邻元素精确对齐时，优先使用相同元素类型（全部 `<span>` 或全部 `<a>`）。`<button>` 在 iOS 上是不可靠的。

### 图片圆角白边

**问题**：卡片模式图片圆角边缘有 1px 白边。

**根因**：`.card-img-area` 的渐变底色从 `border-radius` 圆角边缘透出。

**修复**：`.card-page .card-img-area` 设 `background: transparent`。

---

## 前端交互

### 浏览模式弹出卡改造

- 从单张 AJAX 加载改为一次传入全部 items JSON
- 新增前后翻页按钮 + 计数器（浮在图片上方 + 50% 透明度）
- 图片点击放大，支持滚轮/双指缩放 + 拖拽
- 去掉放大按钮和随机按钮

### 计数器浮层

浏览模式和卡片模式的计数器均使用绝对定位浮在图片上方：
```css
position: absolute; top: 10px; opacity: 0.5; pointer-events: none;
```
`pointer-events: none` 确保不阻挡图片点击缩放。

### 练习模式题目去重

- 同一轮 10 题内：Session 记录已出题目 ID，每题从剩余中抽取
- 跨轮次：上一轮的题目 ID 保留在 Session，新一轮优先排除
- 降级策略：可用题目不够时只排除本轮已出的

### 卡片模式随机起始

`var current = Math.floor(Math.random() * window.cardItems.length)`，每次打开卡片模式从随机位置开始。

---

## 数据 & 后端

### 种子数据（seed_data）

- `ANIMALS` 表格包含 21 只动物的完整数据：中英名、emoji、图片、科普知识、三语音频、手动校准的 `image_position`
- `seed_data --force` 覆盖已有数据；不加 `--force` 时检测到已有数据则跳过
- `image_position_checked=True` 防止 `detect_centers` 覆盖手调值

### N+1 查询修复

`profile_view` 原循环对每个分类逐次查询 `LearningProgress`。改用 `Count + filter=Q()` annotate 一次查询完成。

### view_count 启动 bug

`item_detail_api` 中 `get_or_create` 后 `if progress.id:` 永远为真，导致首次查看就记为 2。改用 `created` 返回值 + `F('view_count') + 1` 原子递增。

---

## 安全

- 登录页 open redirect 加 `url_has_allowed_host_and_scheme` 校验
- `DEBUG` 默认 `False`，`SECRET_KEY` 强制环境变量
- `ALLOWED_HOSTS` 默认 `localhost`
- docker-compose 密码改为环境变量
- 登出改为 POST 表单

---

## 音频

### 音频 404 根因

`FileField.save` 在目标文件已存在时自动追加 `_<7位随机>` 后缀 → DB 与磁盘文件名不一致。

**修复**：`seed_data.py` 改用 `_write_media_file()` 直接以规范纯名覆盖写入，清理随机后缀孤儿。

### iOS 进场自动播放被拦截

`setTimeout` 中 `play()` 脱离用户手势上下文 → `NotAllowedError`。已 `.catch` 静默处理，手动点击不受影响。

---

## CSS 深色模式

- 三态切换：深色(`data-theme=dark`) → 浅色(`data-theme=light`) → 自动(无属性，跟系统)
- 首次访问默认深色
- 所有颜色走 CSS 变量，不要硬编码
- `prefers-reduced-motion` 支持

---

## iPad / Safari 专用坑

### iPad「白变黑」= 智能反转

设置 → 辅助功能 → 显示与文字大小 → 智能反转。**不是 CSS bug**，不要改代码。

### Safari CSS 强缓存

`style.css` 必须带 `?v=` 版本号。

### `<button>` 渲染尺寸偏差

见上文「iOS Safari 渲染差异」一节。用 `<span>` 替代 `<button>` 解决。
