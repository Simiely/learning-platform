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

## 10. 种子数据中的文件复制

**问题**：seed_data 命令从 `media/audio/` 等目录复制文件到 Django 的 MEDIA_ROOT。

**方案**：

```python
from django.core.files.base import ContentFile
with open(src, 'rb') as f:
    item.image.save(img_file, ContentFile(f.read()))
```

`ContentFile` 直接把内存中的字节写入 FileField，避免了手动复制文件的复杂性。
