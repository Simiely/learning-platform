# 增加新动物操作指南 / How to Add New Animals

> 适用项目：learning-platform（Django + Alpine.js 幼儿认知闪卡平台）
> 最后更新：2026-07-30

---

## 📋 完整工作流程概览（重要，请按此顺序执行）

添加新动物分为 **4 个阶段**，必须严格按以下顺序执行：

```
Phase 1 ── 确定动物清单
              │
              ▼
Phase 2 ── 逐只搜索确认图片（串行：一只一只来，所有大图确认完才到下一阶段）
              │
              ▼
Phase 3 ── 批量入库（修改 seed_data.py + 生成音频 + seed_data --force）
              │
              ▼
Phase 4 ── 手工校准 3 种模式的图片焦点
```

---

## Phase 1：确定动物清单

1. 从 `ANIMALS.md` 的「建议新增动物」或新批次规划中确定本次要添加的动物列表
2. 明确每只动物的：中文名、英文名、Emoji、分组、科普知识

---

## Phase 2：逐只搜索确认图片（串行，核心环节）

**一次只处理一只动物，串行执行。**

对清单中的每一只动物：

1. 搜索该动物在 Pexels 上的约 **20 张小图**（参考缩略图，400px）
2. **提交给用户判断**：
   - 用户从 20 张中选中一张 → 下载高清原图（长边 ≥ 3000px），该动物图片确认完成
   - 用户觉得都不满意 → 再搜 20 张小图供选择
   - 重复直到用户确认某张图
3. 确认后才进入 **下一只动物** 的图片搜索

> ⚠️ **关键规则**：所有动物的高清大图都确认完成后，才能进入 Phase 3。

### 素材存放规则

```
new-animals/
├── seaturtle.jpeg       ← 高清原图（选定的最终图片，直接放在根目录）
├── octopus.jpeg
├── ...
└── references/          ← 候选缩略图（找图阶段用，选定后清理）
    ├── seaturtle/       ← 每只动物一个子目录
    ├── octopus/
    └── ...
```

---

## Phase 3：批量入库

### 全部大图确认后，统一执行以下操作：

#### 步骤 1：修改 `seed_data.py`

打开 `apps/core/management/commands/seed_data.py`，在 `ANIMALS` 列表末尾添加新动物元组。

**元组格式**（11 个字段）：

```python
(
    '中文名',                  # name
    '动物名_20260727XX',       # code — 格式：英文小写_日期+序号
    'English Name',           # english_name
    '🐱',                     # emoji
    'animal.{ext}',           # img_file — 图片文件名（原图格式）
    'animal.mp3',             # audio_file — 音频文件名（三个目录共用）
    '科普知识文字...',          # fact — 1-2 句科普
    '50% 50%',                # image_position — iPhone 竖屏焦点（先设默认，Phase 4 校准）
    '50% 50%',                # image_position_ipad_portrait — iPad 竖屏焦点（先设默认）
    '50% 50%',                # image_position_ipad_landscape — iPad 横屏焦点（先设默认）
    'wild',                   # group — 浏览分组（必填）
),
```

**group 字段可选值**：

| 值 | 显示名称 | 含义 | 示例动物 |
|----|---------|------|---------|
| `farm` | 🏠 家里和农场 | 家养/农场动物，孩子日常能接触的 | 狗、猫、马、牛、羊 |
| `wild` | 🌍 野生动物 | 在动物园或自然中看到的动物 | 狮子、老虎、大象、熊猫 |
| `ocean` | 🌊 海洋动物 | 生活在海洋环境中的动物 | 海豚、鲸鱼、鲨鱼、企鹅 |
| `reptile` | 🦎 爬虫和昆虫 | 小型爬行动物和昆虫 | 蛇、鳄鱼、青蛙、蝴蝶 |

**Code 编号规则**：

| 批次 | 日期 | Code 范围 | 动物数量 |
|------|------|-----------|---------|
| 第1批 | 2026-07-23 | `{name}_2026072301` ~ `_2026072321` | 21 |
| 第2批 | 2026-07-24 | `{name}_2026072401` ~ `_2026072420` | 20 |
| 第3批 | 2026-07-29 | `{name}_2026072901` ~ `_2026072912` | 12 |
| 第4批 | 2026-07-29 | `{name}_2026072913` | 1（梅花鹿） |
| 第5批 | 2026-07-29 | `{name}_2026072914` ~ `_2026072920` | 7 |
| 第6批 | 2026-07-30 | `{name}_2026073001` ~ `_2026073006` | 6 |
| 新增 | **当天日期** | `{name}_当天日期XX`（从 01 开始） | 新批次 |

#### 步骤 2：将高清图片放入 `media/images/`

```bash
cp new-animals/{animal}.jpg media/images/{animal}.jpg
```

- **原图格式直出**，不转换格式、不缩放裁剪（jpg / png / webp 等均可）
- **长边 ≥ 3000px**
- 图片文件名与 `seed_data.py` 中 `img_file` 字段保持一致

#### 步骤 3：生成音频（3 种语言）

中文、英文、科普三个音频，文件名相同仅目录不同：

```bash
# 中文发音（仅动物名）
edge-tts --voice zh-CN-XiaoxiaoNeural --text "水母" --write-media media/audio/jellyfish.mp3

# 英文发音（仅动物名）
edge-tts --voice en-US-JennyNeural --text "Jellyfish" --write-media media/audio_en/jellyfish.mp3

# 科普发音（全文朗读）
edge-tts --voice zh-CN-XiaoxiaoNeural --text "水母没有大脑、没有心脏、没有血液..." --write-media media/audio_fact/jellyfish.mp3
```

> 三个文件名必须完全一致，仅目录不同

#### 步骤 4：运行种子命令

```bash
python manage.py seed_data --force
```

`--force` 会清空已有数据并重新导入所有动物（包括新旧）。

#### 步骤 5：更新 `ANIMALS.md`

添加新批次表格，更新快速筛选表中的批次和总数。

---

## Phase 4：手工校准图片焦点

所有数据入库后，**用户手动**调整 3 种模式的图片中心：

| 焦点字段 | 对应设备 | 说明 |
|---------|---------|------|
| `image_position` | **iPhone 竖屏** | 手机竖屏时的显示焦点 |
| `image_position_ipad_portrait` | **iPad 竖屏** | iPad 竖屏时的显示焦点 |
| `image_position_ipad_landscape` | **iPad 横屏** | iPad 横屏时的显示焦点 |

### 校准原则

1. **焦点对准头部/面部** — 动物的眼睛或脸部是视觉中心
2. **iPhone 焦点** — 通常是动物头部位置
3. **iPad 竖屏** — 画面更宽，动物位置可能需要左右调整
4. **iPad 横屏** — 画面最宽，动物可能偏左或偏右，需要大幅调整
5. **纵向补偿** — `centerPos()` 函数会自动对纵向做 ×0.65 上偏补偿
6. **有效范围**：5%~95% 之间

> ⚠️ **已有动物的图片焦点已手工校准，禁止擅自修改**

---

## 文件清单速查

修改/新增的文件：

```
需要修改:
  apps/core/management/commands/seed_data.py    ← ANIMALS 列表加新元组（11个字段，含 group）
  ANIMALS.md                                     ← 文档更新

需要新增（每只动物）:
  media/images/{animal}.jpg                      ← 图片
  media/audio/{animal}.mp3                       ← 中文音频
  media/audio_en/{animal}.mp3                    ← 英文音频
  media/audio_fact/{animal}.mp3                  ← 科普音频
```

**无需修改的文件**（系统自动适配）：

```
  apps/core/models.py           — Item 模型已有完整字段
  apps/core/views.py            — 视图自动从 DB 加载所有 Item
  templates/*.html              — 模板自动渲染所有 Item
  static/js/*.js                — JS 逻辑与数据量无关
  static/css/*.css              — 样式自动适应
```

---

## Pexels 图片搜索与下载

> 推荐使用 Pexels（免费可商用）。Pexels 网站有 Cloudflare 反爬保护，需用 Playwright + stealth。

### 搜索参考缩略图（Phase 2 用）

```bash
pip install playwright playwright-stealth
python -m playwright install chromium
```

搜索脚本见 `scripts/pexels_search.py`，替换动物名即可使用。

### 下载高清原图（用户确认后）

```python
import urllib.request, ssl

pid = 3046629  # 用户选中的 Pexels 照片 ID
url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx))

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = opener.open(req, timeout=30).read()
with open(f"media/images/{animal}.jpg", 'wb') as f:
    f.write(data)
```

> 不加 `?w=` 参数就是原始分辨率，确保长边 ≥ 3000px。

---

## 音频生成方式

使用 edge-tts（Microsoft Edge 内置神经网络语音），免费、无需 API Key。

| 用途 | 推荐语音 | 说明 |
|------|---------|------|
| 中文（动物名 + 科普） | `zh-CN-XiaoxiaoNeural` | 女声，自然清晰 |
| 英文（动物名） | `en-US-JennyNeural` | 美式女声 |

```bash
pip install edge-tts
```

---

## 调试和验证

1. **检查焦点**：运行 `python manage.py runserver`，在浏览器中查看各模式下的图片显示
2. **检查分组**：在浏览模式页面顶部查看 Tabs，确认新动物出现在正确的分组中
3. **检查排序**：确认拼音排序正确
4. **音频文件**：确认三个目录都有对应文件，否则播放按钮会变灰色

### 验证分组数量

```bash
python manage.py shell -c "
from django.db.models import Count
from apps.core.models import Item
for g, cnt in Item.objects.values('group').annotate(c=Count('id')).order_by('group'):
    print(f'{g or \"(无)\"}: {cnt}只')
"
```
