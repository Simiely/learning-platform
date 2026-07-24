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

- `ANIMALS` 表格包含 **41 只动物**的完整数据：中英名、emoji、图片、科普知识、三语音频、iPhone 焦点 + iPad 焦点
- 每行 8 字段：`(name, en_name, emoji, img_file, audio_file, fact, image_position, image_position_ipad)`
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

### gTTS 代理问题 → 改用 edge-tts（2026-07-24）

**问题**：沙箱网络走代理 `127.0.0.1:7890`，gTTS（Google Text-to-Speech）请求 Google 翻译 API 被代理拦截，连续超时。

**排查过程**：
1. 不设代理 → DNS 解析失败（沙箱无直连外网权限）
2. 设代理 → 部分请求能通但极不稳定，批量 20 只动物跑几分钟后随机断开
3. 尝试 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量全部无效

**修复**：改用 **edge-tts**（Microsoft Edge 内置神经网络语音，调用 `cognitive.microsoft.com`）：
```python
import asyncio
from edge_tts import Communicate

async def gen():
    await Communicate('考拉', voice='zh-CN-XiaoxiaoNeural').save('audio/koala.mp3')
    await Communicate('Koala', voice='en-US-JennyNeural').save('audio_en/koala.mp3')
asyncio.run(gen())
```
- 不走 Google，代理可通，稳定快速
- 中文：`zh-CN-XiaoxiaoNeural`（自然女声）
- 英文：`en-US-JennyNeural`（美式女声）
- `pip install edge-tts` 即可使用

**教训**：沙箱环境优先使用不依赖 Google 的 TTS。edge-tts 走 Azure 流，对代理友好。

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

### Safari Tracking Prevention 导致 CDN 脚本卡顿（2026-07-23）

**现象**：练习模式突然变得非常卡顿，控制台报 `Tracking Prevention blocked access to storage for https://cdn.jsdelivr.net/...alpinejs...`

**根因**：Safari 智能追踪防护阻止了 CDN 域的 Alpine.js 访问 localStorage/Web Storage，导致脚本执行挂起。

**修复**：将 Alpine.js 从 CDN 下载到 `static/js/alpine.min.js`，模板改用 `{% static 'js/alpine.min.js' %}`。同域静态文件不受追踪防护限制。

**教训**：关键 JS 库不要用 CDN，下载到项目本地托管更可靠。

### 练习模式按钮溢出裁剪（2026-07-23）

**现象**：「下一题」按钮贴边甚至超出可视范围，容器 `overflow: hidden` 裁剪底部。

**根因**：`quiz-feedback` 高度（70px）小于实际内容需求。内容 = padding(8) + 文字区(24px) + 按钮 margin(4px) + 按钮高度(~44px) + padding-bottom(8) = 88px。

**完整布局链**：
```
container-card (height: calc(100vh-52px), overflow:hidden)
  quiz-body (flex:1)
    quiz-round (flex:1, min-height:0)
      quiz-img (flex:1, min-height:0)
      quiz-options (flex:none, ~118px)
      quiz-feedback (flex:none, 必须 ≥ 88px)
```

**修复**：`quiz-feedback` 高度设为 90px，确保内容不溢出。任何高度调整需验证 `∑(flex:none) ≤ height(container-card)`。

### 练习答题后自动朗读（2026-07-23）

`selectAnswer()` 调用 `playQuizAudio()` → 播放中文音频 → 1s 后播放英文。
需要 API 返回 `audio_zh`、`audio_en` 字段，前端用 `<audio>` 元素播放。
`play()` 用 `.catch` 静默处理 iOS 自动播放拦截。

### 图片容器统一透明背景（2026-07-23）

`.popup-img`、`.card-img-area`、`.quiz-img` 全部设 `background: transparent`。
消除渐变底色从 `border-radius` 圆角边缘透出的 1px 白边。

### 练习结果大字报排版（2026-07-23）

- 显示「对了 X 个」，数字 64px，「对了」「个」28px
- 满分：「🎉 满分！太厉害了！」
- 6-9 个：「不错，继续加油」
- 结果区 `padding-top: 60px` 下移避免太靠上

### 答对礼花特效（2026-07-23）

纯 JS Canvas 粒子爆炸：80 颗彩色圆点从图片底部边缘为中心向四周炸开，带重力下坠 + 渐隐。
`launchConfetti()` 在 `selectAnswer` 答对时触发。

### Docker 部署媒体同步策略（2026-07-23）

**问题**：更新了种子数据中的图片焦点、替换了媒体文件（如鸭图），但 Docker 部署后不生效。

**根因分析**：
1. **图片焦点**：`seed_data` 只在数据库为空时运行，已有数据容器直接跳过 → `sync_positions` 命令每次启动从 seed_data 同步
2. **媒体文件**：之前 `ensure_media` 从 GitHub tarball 下载，已存在就跳过；且 `.dockerignore` 排除了 `media/`，镜像内没有媒体文件

**修复**：
- `.dockerignore` 去掉 `media/`，让镜像自带媒体
- Dockerfile 构建时 `cp` 一份 `/app/media-bundled`
- entrypoint 用 `rsync -ac` 从 bundled 同步到卷，checksum 比较只传变化文件
- 新增 `sync_positions` 命令，每次启动更新 image_position 字段

### 浏览弹窗自动发音（2026-07-23）

`showPopup()` → 300ms 后播中文 → 1300ms 后播英文，与卡片模式时序一致。
`playBrowseAudio` 播放前先 `pause()` + `removeAttribute('src')` 避免音频冲突。

### iPad 双击缩放禁用（2026-07-23）

viewport meta 加 `user-scalable=no`，阻止浏览器默认双击缩放。
应用内图片缩放（CSS transform）不受影响。

### Web Audio API 合成音效（2026-07-23）

答对/答错/翻卡音效用 Web Audio API OscillatorNode 合成，不需要额外音频文件。
- 答对：3个上升正弦波（C5-E5-G5），清脆悦耳
- 答错：正弦波 440Hz→300Hz 平滑下降，柔和提示
- AudioContext 在用户点击回调中创建，iOS 不会拦截

### Canvas 礼花在 iPad 上卡顿（2026-07-23）

**现象**：电脑流畅，iPad 卡顿。

**根因**：iPad Retina 屏 devicePixelRatio=2，canvas 没有适配 DPR。浏览器在后台做隐式缩放，消耗 GPU。

**修复**：canvas 尺寸 = 逻辑像素 × DPR（上限2），ctx.scale(dpr, dpr) 映射坐标。CSS 尺寸保持逻辑像素。

### 动物数据清单（2026-07-23）

`ANIMALS.md` 是所有动物数据的主数据源（21 已上线 + 20 新增 = 共 41 只）。
修改动物内容（增减、科普、焦点）先编辑这个文件，再同步到 `seed_data.py`。

**焦点调整工作流**（2026-07-24 优化）：
- 所有焦点都是基于中心 `50% 50%` 的相对偏移
- 修改 `seed_data.py` → `python manage.py seed_data --force` 刷新数据库
- 服务不需要重启，刷新前端页面即可

### iPad / iPhone 双套图片焦点（2026-07-24）

**需求**：iPad 横/竖屏和 iPhone 竖屏的图片构图不同，需要各自独立的视觉焦点。

**实现**：
1. **模型** `Item` 新增 `image_position_ipad` 字段（`CharField, default='50% 50%'`）
2. **迁移** `0009_item_image_position_ipad`（makemigrations → migrate）
3. **API** `to_dict()` 和 `quiz_question_api()` 同时返回 `image_position` 和 `image_position_ipad`
4. **seed_data** 每个动物增加第 8 个参数（默认为 iPhone 焦点值）
5. **ANIMALS.md** 新增「焦点(iPad)」列

**注意**：前端尚未实现 iPad 检测切换。后期只需一行 JS `screenWidth >= 768` 选择对应字段即可。

### 中文文件名 → 英文重命名（2026-07-24）

**问题**：Windows 下用户拖入的文件名是中文（如 `北极熊.jpg`），需要批量改成英文。

**教训**：
- 不能用 Bash 的 `mv`（UTF-8 over Git Bash 处理中文文件名编码混乱）
- Bash 的 `rename` 命令不可用（需 Linux 的 util-linux 版本）
- **必须用 PowerShell**：
  ```powershell
  Rename-Item "北极熊.jpg" "polarbear.jpg"
  ```
  PowerShell 原生支持 Unicode 路径名，不会编码损坏。

### 新增 20 只动物的批量工作流（2026-07-24）

完整记录了一次批量添加 20 只动物的端到端流程：

**阶段 1：图片素材**
1. 从 Pexels 搜索页（`pexels.com/search/<animal>/`）批量提取 photo ID
2. 用 Python 下载 400px 缩略图到 `candidates/`
3. 用户逐个挑选，有时需要换搜索词（如蛇：不要特写 → 普通搜索）
4. 确定后下载高清原图（不 `?w=` 参数 = 原始分辨率）
5. 保存到 `media/images/`，清理 `candidates/`

**阶段 2：音频生成**
1. 安装 `edge-tts`（pip install edge-tts）
2. 异步批量生成 `audio/`（中文名）、`audio_en/`（英文名）、`audio_fact/`（科普）
3. 约 1-2 秒/个，20 只 × 3 = 60 个文件约 2 分钟

**阶段 3：数据整合**
1. `ANIMALS.md` 新增 20 行，标记 ✅
2. `seed_data.py` 追加 20 条元组
3. `python manage.py seed_data --force` 写入数据库
4. 手动校准图片焦点（用户反馈 → 调整值 → 重跑 seed_data）

**阶段 4：清理**
- 删除 `new-animals/` 临时目录
- 删除 `candidates/` 缩略图
- 删除调试脚本（`gen_audio.py` 等）

### 新增动物图片素材下载工作流（2026-07-24）

**流程**：缩略图挑选 → 用户选择 → 高清下载 → 入仓

1. **批量下载缩略图**（Pexels / Pixabay，免费商用）

   - 搜索关键词用**纯英文**（如 `polar-bear` 而非 `北极熊`）
   - 从 Pexels 搜索结果页 HTML 提取 photo ID（需 User-Agent 伪装）
   - 下载 400px 缩略图到 `new-animals/images/candidates/`

   ```python
   # Pexels 直接访问图片 CDN 不需要搜索页权限
   # 通过已知 photo ID 下载缩略图
   import urllib.request, ssl, io, os
   from PIL import Image
   ctx = ssl.create_default_context()
   ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
   handler = urllib.request.ProxyHandler({'https': 'http://127.0.0.1:7890'})
   opener = urllib.request.build_opener(handler, urllib.request.HTTPSHandler(context=ctx))

   for pid in photo_ids:
       url = f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=400'
       req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
       resp = opener.open(req, timeout=10)
       img = Image.open(io.BytesIO(resp.read()))
       img.save(f'new-animals/images/candidates/{label}.jpg')
   ```

2. **用户挑选后下载高清原图**
   ```python
   url = f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg'
   # 不加 w 参数 = 原始分辨率
   ```

3. **裁剪正方形 + 长边 ≥ 3000px**

4. **清理候选项**

**注意**：
- Pexels 搜索页会 403，但图片 CDN（`images.pexels.com`）可以直接访问
- 沙箱网络问题用调试 Python：`C:\Users\2504\.workbuddy\binaries\python\versions\3.13.12\python.exe` + ProxyHandler
- 关键词必须英文，Pexels URL 用连字符（`polar-bear`）
