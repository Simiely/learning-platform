# 增加新动物操作指南 / How to Add New Animals

> 适用项目：learning-platform（Django + Alpine.js 幼儿认知闪卡平台）
> 最后更新：2026-07-29

---

## 文件存放规则

新动物的所有素材统一放在 `new-animals/` 目录下，按以下结构组织：

```
new-animals/
├── seaturtle.jpeg       ← 高清原图（选定的最终图片，直接放在根目录）
├── octopus.jpeg
├── ...
└── references/          ← 参考缩略图（找图阶段的候选小图，选定后清理）
    ├── seaturtle/
    ├── octopus/
    ├── seahorse/
    └── ...
```

- **最终图片**: `new-animals/{animal}.{ext}` — 直接放在根目录，原图格式，不裁剪缩放
- **参考图**: `new-animals/references/{animal}/` — 找图阶段的 400px 缩略图，选好大图后清理
- **音频不放入该目录**：音频直接生成到 `media/audio/`、`media/audio_en/`、`media/audio_fact/`
- 等所有新动物素材就绪后，再集中编辑 `seed_data.py` 并入库

---

## 一、你需要准备的材料（每只动物）

| 项目 | 说明 | 样例 |
|------|------|------|
| 中文名 | 动物中文名称 | 狮子 |
| 英文名 | 动物英文名称 | Lion |
| Emoji | 对应的 Emoji 字符 | 🦁 |
| 图片 | 一张高质量动物照片（原图格式） | `lion.jpg` |
| 科普知识 | 1-2 句有趣科普（约 40-80 字） | 狮子是唯一群居的猫科动物... |
| 分组 | 浏览分组（farm/wild/ocean/reptile） | `wild` |
| 音频（中） | 中文发音：仅读动物名 | `lion.mp3` (内容：狮子) |
| 音频（英） | 英文发音：仅读动物名 | `lion.mp3` (内容：Lion) |
| 音频（科普） | 科普知识全文朗读 | `lion.mp3` (内容：狮子是唯一...) |

> **注意**：三个音频的文件名相同但放在不同目录。当前项目使用 edge-tts 生成。

---

## 二、3 个图片焦点（非常重要 ⭐）

每只动物需要校准 **3 个图片焦点**，控制动物在图片中的显示位置（CSS `object-position`）。格式为 `"X% Y%"`，如 `"56% 28%"`。

### 焦点含义

```
  X%        水平位置：0%（左）← → 100%（右）
  Y%        垂直位置：0%（上）← → 100%（下）
```

### 三个焦点的用途

| 焦点字段 | 对应设备 | 说明 |
|---------|---------|------|
| `image_position` | **iPhone 竖屏** | 手机竖屏时的显示焦点 |
| `image_position_ipad_portrait` | **iPad 竖屏** | iPad 竖屏（屏幕宽 < 高）时的显示焦点 |
| `image_position_ipad_landscape` | **iPad 横屏** | iPad 横屏（屏幕宽 > 高）时的显示焦点 |

### 校准原则

1. **焦点对准头部/面部** — 动物的眼睛或脸部是视觉中心
2. **iPhone 焦点** — 通常是动物头部位置
3. **iPad 竖屏** — 画面更宽，动物位置可能需要左右调整（部分往右偏移 10-15%）
4. **iPad 横屏** — 画面最宽，动物可能偏左或偏右，需要大幅调整
5. **纵向补偿** — 在卡片模式下，`centerPos()` 函数会自动对纵向做 ×0.65 上偏补偿（所以初始 Y 值可以偏下一些）
6. **有效范围**：5%~95% 之间

### 常见场景示例

```python
# 动物居中 → 三个焦点相同
('50% 50%', '50% 50%', '50% 50%')

# 动物在画面上半部分 → iPhone 和 iPad 需要不同水平偏移
('56% 28%', '56% 28%', '56% 38%')    # iPad 横屏往下调 10%

# 动物偏左 → iPad 横屏需要右移视图
('35% 50%', '35% 50%', '50% 50%')    # iPad 横屏右移 15%

# 动物偏右 → iPad 模式需要调整
('85% 50%', '95% 50%', '95% 50%')    # iPad 都往右多移一点
```

---

## 三、代码修改步骤

### 步骤 1：修改 `seed_data.py`

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
    '50% 50%',                # image_position — iPhone 竖屏焦点
    '50% 50%',                # image_position_ipad_portrait — iPad 竖屏焦点
    '50% 50%',                # image_position_ipad_landscape — iPad 横屏焦点
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

**分组选择指南**（避免交叉）：
- 企鹅 → `ocean`（关联南极/海洋/冰块，而非鸟类）
- 鹰/猫头鹰/鹦鹉 → `wild`（在自然或动物园中见到）
- 鳄鱼 → `reptile`（爬行动物）
- 松鼠 → `wild`（森林野生动物）
- 蜜蜂/蝴蝶 → `reptile`（与爬虫归为一类展示）

**Code 编号规则**：

| 批次 | 日期 | Code 范围 | 动物数量 |
|------|------|-----------|---------|
| 第1批 | 2026-07-23 | `{name}_2026072301` ~ `_2026072321` | 21 |
| 第2批 | 2026-07-24 | `{name}_2026072401` ~ `_2026072420` | 20 |
| 第3批 | 2026-07-29 | `{name}_2026072901` ~ `_2026072912` | 12 |
| 新增 | **当天日期** | `{name}_当天日期XX`（从 01 开始） | 新批次 |

### 步骤 2：添加图片文件

```
media/images/{animal}.{ext}
```

- **原图格式直出**，不转换格式、不缩放裁剪（jpg / png / webp 等均可）
- **长边 ≥ 3000px**，避免下载到缩略图小图
- 动物面部清晰可见
- 图片文件名与 `seed_data.py` 中 `img_file` 字段保持一致

### 步骤 2.5：从 Pexels 下载图片素材

> 推荐使用 Pexels（免费可商用）。Pexels 网站有 Cloudflare 反爬保护，不能用 requests/urllib 直接访问，需要用 **Playwright + stealth**（真实浏览器模拟）绕过。

**完整工作流**：

```
Playwright 自动化搜索 → 下载确认描述的缩略图（24张+）→ 挑选最佳 → 下高清原图入库
```

---

#### 阶段 A：Playwright 自动搜索并下载参考缩略图

**前置条件**（首次使用需安装）：

```bash
pip install playwright playwright-stealth
python -m playwright install chromium
```

**搜索脚本**（替换 `animal` 名称即可使用）：

```python
import asyncio, os, urllib.request, ssl
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def search_pexels(animal):
    out_dir = f"new-animals/{animal}/reference"
    os.makedirs(out_dir, exist_ok=True)

    stealth = Stealth()
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": "http://127.0.0.1:7890"},  # 沙箱代理
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        await stealth.apply_stealth_async(context)
        page = await context.new_page()

        url = f"https://www.pexels.com/search/{animal}/"
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)  # 等页面渲染

        # 提取照片 ID + 描述
        photos = await page.evaluate("""() => {
            const results = [];
            const seen = new Set();
            const links = document.querySelectorAll('a[href*="/photo/"]');
            for (const a of links) {
                const match = a.getAttribute('href').match(/\\/photo\\/[^/]+-(\\d+)/);
                if (!match || seen.has(match[1])) continue;
                seen.add(match[1]);
                const img = a.querySelector('img');
                results.push({
                    id: parseInt(match[1]),
                    alt: img ? (img.getAttribute('alt') || '') : '',
                });
            }
            return results;
        }""")

        # 滚动加载更多
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
        # 重复提取（scroll 后新加载的）
        # ...（同上 evaluate）

        # 下载缩略图（400px）
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_ctx))

        for i, p in enumerate(photos):
            thumb = f"https://images.pexels.com/photos/{p['id']}/pexels-photo-{p['id']}.jpeg?w=400"
            path = os.path.join(out_dir, f"{i+1:03d}_{p['id']}.jpg")
            req = urllib.request.Request(thumb, headers={'User-Agent': 'Mozilla/5.0'})
            data = opener.open(req, timeout=10).read()
            with open(path, 'wb') as f:
                f.write(data)

        await browser.close()
        print(f"Downloaded {len(photos)} images to {out_dir}")

asyncio.run(search_pexels("octopus"))  # ← 替换动物名
```

> ⚠️ 关键点：
> - **必须用 `playwright-stealth`** 绕过 Cloudflare 指纹检测（普通 Playwright 会被拦截）
> - 浏览器必须配置沙箱代理 `proxy={"server": "http://127.0.0.1:7890"}`
> - Pexels CDN 下载缩略图不用代理，直接直连
> - 每个照片附带了 `alt` 描述，可以确认是否匹配目标动物
> - 会自动翻页加载，可以拿到 20-30 张

---

#### 方案 B：Pexels 官方 API（推荐，更高效）

> 注册 [pexels.com/api](https://www.pexels.com/api/) 获取免费 API Key → 不限速、可翻页、结构化 JSON。

```bash
pip install requests
```

```python
import requests

API_KEY = "你的API_KEY"
headers = {"Authorization": API_KEY}

# 搜索：每页 20 张，page=1（不要多翻页，防限流）
url = f"https://api.pexels.com/v1/search?query=hedgehog&per_page=20&page=1"
data = requests.get(url, headers=headers).json()
print(f"Total: {data['total_results']}")
for p in data["photos"]:
    print(f"ID:{p['id']}  {(p.get('alt') or '')[:55]}")

# 下载缩略图（CDN 直连，不用 API Key）
thumb = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?w=400"
```

> ⚠️ **API 限流警告（重要）**：
> - Pexels 免费版 **每月仅 200 次请求**额度
> - 一次 `per_page=80&page=3` 就用了 240 次，**直接刷爆月度配额**，后续所有请求返回 403 Forbidden
> - **务必节约**：每次搜索只取 **1 页（page=1, per_page=20）**，找到好图就停，不重复翻页
> - 配额 **每月重置** / 升级付费版可提额

---

#### 阶段 B：挑选后下载高清原图

从 `new-animals/{animal}/reference/` 挑出最好的一张，下高清原图到 `new-animals/{animal}/full/`：

```python
import urllib.request, ssl, os

pid = 3046629  # ← 替换为你选中的 Pexels 照片 ID
url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"  # 不加 ?w= 参数 = 原图

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx))

out = f"new-animals/octopus/full/octopus.jpeg"
os.makedirs(os.path.dirname(out), exist_ok=True)

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = opener.open(req, timeout=30).read()
with open(out, 'wb') as f:
    f.write(data)

from PIL import Image
import io
img = Image.open(io.BytesIO(data))
print(f"Downloaded {len(data)/1024:.0f} KB, {img.width}x{img.height}px")
# 确认长边 >= 3000px 即可

你从 `references/{animal}/` 的 12 张中挑出最好的（通常 1 张），然后下高清原图到 `media/images/`：

```python
# 高清原图（不加 ?w= 参数 = 原始分辨率）
url = f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
# 保存到 media/images/{animal}.{ext}
```

> 确认原图长边 ≥ 3000px，满足图片要求。

### 步骤 3：添加音频文件（3 个文件）

```
media/audio/{animal}.mp3       # 中文发音（仅动物名）
media/audio_en/{animal}.mp3    # 英文发音（仅动物名）
media/audio_fact/{animal}.mp3  # 科普发音（全文朗读）
```

**文件名必须完全一致**，仅目录不同。当前使用 edge-tts 生成。

### 步骤 4：运行种子命令

```bash
python manage.py seed_data --force
```

`--force` 会清空已有数据并重新导入所有动物（包括新旧）。

### 步骤 5：更新文档

更新 `ANIMALS.md`，添加新动物的完整信息。

---

## 四、文件清单速查

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

## 五、现有动物数据样例（供参考格式）

### 第一批（21 只）— Code 后缀 `_20260723XX`

```python
('狮子', 'lion_2026072301', 'Lion', '🦁', 'lion.jpg', 'lion.mp3', '狮子是唯一群居的猫科动物，一个狮群通常由1-2头雄狮和几头母狮组成。雄狮的鬃毛越浓密越受母狮青睐。', '13% 47%', '23% 37%', '23% 47%'),
('大象', 'elephant_2026072302', 'Elephant', '🐘', 'elephant.jpg', 'elephant.mp3', '大象是陆地上最大的哺乳动物。它们的鼻子由超过4万块肌肉组成，既能拔起大树也能捡起一粒花生。', '58% 63%', '58% 63%', '58% 73%'),
('熊猫', 'panda_2026072303', 'Panda', '🐼', 'panda.jpg', 'panda.mp3', '大熊猫是中国国宝，虽然属于食肉目，但99%的食物都是竹子，每天要花12-16小时进食。', '46% 25%', '46% 25%', '46% 35%'),
('老虎', 'tiger_2026072304', 'Tiger', '🐯', 'tiger.jpg', 'tiger.mp3', '老虎是世界上最大的猫科动物，每只老虎身上的条纹都是独一无二的，就像人类的指纹一样。', '42% 54%', '52% 54%', '52% 54%'),
('长颈鹿', 'giraffe_2026072305', 'Giraffe', '🦒', 'giraffe.jpg', 'giraffe.mp3', '长颈鹿是地球上最高的陆地动物，脖子虽然很长，但颈椎骨数量和人类一样都是7块。', '49% 5%', '49% 15%', '49% 15%'),
('斑马', 'zebra_2026072306', 'Zebra', '🦓', 'zebra.jpg', 'zebra.mp3', '斑马的黑白条纹不仅是伪装，还能防蚊虫叮咬。每只斑马的条纹图案都是独一无二的。', '62% 58%', '47% 58%', '62% 58%'),
('企鹅', 'penguin_2026072307', 'Penguin', '🐧', 'penguin.jpg', 'penguin.mp3', '企鹅是鸟类中的游泳高手，帝企鹅可以潜入500米深的海水中，憋气超过20分钟。', '46% 15%', '46% 15%', '46% 15%'),
('海豚', 'dolphin_2026072308', 'Dolphin', '🐬', 'dolphin.jpg', 'dolphin.mp3', '海豚是非常聪明的海洋哺乳动物，它们用超声波定位和交流，睡觉时大脑一半休息一半保持清醒。', '42% 20%', '42% 50%', '42% 30%'),
('猴子', 'monkey_2026072309', 'Monkey', '🐵', 'monkey.jpg', 'monkey.mp3', '猴子是灵长类动物中种类最丰富的一类，它们有复杂的社会结构，会使用工具和互相梳理毛发。', '45% 32%', '45% 92%', '45% 42%'),
('兔子', 'rabbit_2026072310', 'Rabbit', '🐰', 'rabbit.jpg', 'rabbit.mp3', '兔子的耳朵可以转动270度，帮助它们听到远处的危险。它们高兴时会跳起来在空中转身，这叫binky。', '45% 23%', '45% 23%', '45% 23%'),
('猫', 'cat_2026072311', 'Cat', '🐱', 'cat.jpg', 'cat.mp3', '猫是世界上最受欢迎的宠物之一。它们的胡须能感知空气的细微变化，帮助它们在黑暗中判断方向。', '56% 28%', '56% 28%', '56% 38%'),
('狗', 'dog_2026072312', 'Dog', '🐶', 'dog.jpg', 'dog.mp3', '狗是人类最早驯化的动物，它们的嗅觉比人类灵敏1万到10万倍，能嗅出疾病和情绪变化。', '49% 29%', '49% 29%', '49% 29%'),
('马', 'horse_2026072313', 'Horse', '🐴', 'horse.jpg', 'horse.mp3', '马可以站着睡觉，但需要躺下才能进入深度睡眠。它们的视野差不多达到360度。', '59% 66%', '34% 66%', '49% 66%'),
('牛', 'cow_2026072314', 'Cow', '🐮', 'cow.jpg', 'cow.mp3', '牛有四个胃室来消化草料，它们能看到颜色，而且对红色其实并不敏感。', '28% 54%', '38% 54%', '38% 54%'),
('羊', 'sheep_2026072315', 'Sheep', '🐑', 'sheep.jpg', 'sheep.mp3', '绵羊有极好的记忆力，能记住50多张面孔长达两年。它们还能通过面部表情识别同伴的情绪。', '48% 60%', '48% 60%', '48% 60%'),
('鸡', 'chicken_2026072316', 'Chicken', '🐔', 'chicken.jpg', 'chicken.mp3', '鸡是世界上最常见的鸟类，全球养殖数量超过250亿只。它们能用超过30种不同的叫声来交流。', '54% 6%', '54% 6%', '54% 6%'),
('鸭子', 'duck_2026072317', 'Duck', '🦆', 'duck.jpg', 'duck.mp3', '鸭子的脚掌不会感到冷，因为它们脚上的血管排列特殊，能回收热量。小鸭子会把出生后看到的第一个移动物体当妈妈。', '32% 71%', '32% 71%', '32% 91%'),
('鱼', 'fish_2026072318', 'Fish', '🐟', 'fish.jpg', 'fish.mp3', '鱼类是地球上最古老的脊椎动物，已经存在超过5亿年。有些鱼能改变性别，有些能发电。', '87% 44%', '87% 44%', '87% 44%'),
('蝴蝶', 'butterfly_2026072319', 'Butterfly', '🦋', 'butterfly.jpg', 'butterfly.mp3', '蝴蝶用脚来尝味道！它们的翅膀上覆盖着细小的鳞片，这些鳞片能反射光线产生绚丽的色彩。', '54% 56%', '64% 56%', '54% 56%'),
('青蛙', 'frog_2026072320', 'Frog', '🐸', 'frog.jpg', 'frog.mp3', '青蛙的皮肤可以吸收水分和氧气，所以它们对环境污染特别敏感。它们是环境健康的"指示物种"。', '53% 56%', '33% 56%', '53% 56%'),
('鲨鱼', 'shark_2026072321', 'Shark', '🦈', 'shark.jpg', 'shark.mp3', '鲨鱼比恐龙出现的时间还早，已经在地球上生存超过4亿年。它们一生会换掉超过3万颗牙齿。', '85% 50%', '95% 50%', '95% 50%'),
```

### 第二批（20 只）— Code 后缀 `_20260724XX`

```python
('北极熊', 'polar_bear_2026072401', 'Polar Bear', '🐻‍❄️', 'polarbear.jpg', 'polarbear.mp3', '北极熊的皮肤其实是黑色的，毛发是透明的，看起来白色是因为反射了光线。它们是游泳高手，能连续游好几天。', '35% 50%', '25% 50%', '35% 50%'),
('豹子', 'leopard_2026072402', 'Leopard', '🐆', 'leopard.jpg', 'leopard.mp3', '豹子是短跑冠军，最高时速可达120公里。它们会把猎物拖到树上保存，防止被其他动物偷走。', '35% 50%', '35% 50%', '35% 50%'),
('袋鼠', 'kangaroo_2026072403', 'Kangaroo', '🦘', 'kangaroo.jpg', 'kangaroo.mp3', '袋鼠宝宝出生时只有花生米大小，会在妈妈的育儿袋里继续发育半年以上。袋鼠只会向前跳不会向后退。', '60% 50%', '50% 50%', '50% 50%'),
('鳄鱼', 'crocodile_2026072404', 'Crocodile', '🐊', 'crocodile.jpg', 'crocodile.mp3', '鳄鱼是恐龙时代的幸存者，已经在地球上生存超过2亿年。它们的大颚咬合力是所有动物中最强的。', '95% 50%', '85% 50%', '65% 50%'),
('河马', 'hippo_2026072405', 'Hippo', '🦛', 'hippo.jpg', 'hippo.mp3', '河马的皮肤会分泌一种红色的"防晒霜"，既能防晒又能抗菌。虽然看起来笨重，它们跑起来比人还快。', '85% 50%', '70% 50%', '70% 50%'),
('狐狸', 'fox_2026072406', 'Fox', '🦊', 'fox.jpg', 'fox.mp3', '狐狸是聪明机灵的猎手，它们能听到地下老鼠的动静。北极狐的皮毛会随季节变色：冬天白色，夏天棕色。', '65% 50%', '100% 50%', '65% 60%'),
('鲸鱼', 'whale_2026072407', 'Whale', '🐋', 'whale.jpg', 'whale.mp3', '蓝鲸是地球上最大的动物，心脏有一辆小汽车那么大。鲸鱼的歌声可以在海洋中传播数百公里。', '30% 50%', '30% 50%', '30% 50%'),
('考拉', 'koala_2026072408', 'Koala', '🐨', 'koala.jpg', 'koala.mp3', '考拉每天要睡18-22��小时，它们只吃桉树叶，而且能从树叶中获取大部分水分，几乎不喝水。', '50% 50%', '25% 50%', '35% 50%'),
('狼', 'wolf_2026072409', 'Wolf', '🐺', 'wolf.jpg', 'wolf.mp3', '狼是高度社会化的动物，狼群有严格的等级制度。它们的嚎叫可以和数公里外的同伴沟通。', '50% 50%', '50% 125%', '50% 75%'),
('骆驼', 'camel_2026072410', 'Camel', '🐫', 'camel.jpg', 'camel.mp3', '骆驼的驼峰里储存的不是水而是脂肪，它们一次能喝下100升水，可以连续几天不喝水穿越沙漠。', '50% 50%', '20% 50%', '60% 50%'),
('猫头鹰', 'owl_2026072411', 'Owl', '🦉', 'owl.jpg', 'owl.mp3', '猫头鹰的头可以转动270度，因为它们有14节颈椎骨（人类只有7节）。它们能在完全黑暗中捕猎。', '50% 40%', '50% 40%', '50% 20%'),
('蜜蜂', 'bee_2026072412', 'Bee', '🐝', 'bee.jpg', 'bee.mp3', '一只蜜蜂一生只能产出约一茶匙的蜂蜜。它们通过跳"8字舞"来告诉同伴花朵的位置和距离。', '55% 50%', '55% 50%', '55% 50%'),
('螃蟹', 'crab_2026072413', 'Crab', '🦀', 'crab.jpg', 'crab.mp3', '螃蟹横着走路是因为它们的腿关节只能向侧面弯曲。它们会脱壳长大，脱壳后身体是软的容易受伤。', '45% 50%', '45% 50%', '45% 50%'),
('蛇', 'snake_2026072414', 'Snake', '🐍', 'snake.jpg', 'snake.mp3', '蛇没有眼睑，所以它们永远睁着眼睛睡觉。它们用分叉的舌头来"闻"空气中的气味。', '50% 50%', '50% 50%', '50% 50%'),
('松鼠', 'squirrel_2026072415', 'Squirrel', '🐿️', 'squirrel.jpg', 'squirrel.mp3', '松鼠每年会埋藏上千颗坚果，虽然它们会忘记其中很多藏匿点，但这些被遗忘的坚果会发芽长成新树。', '55% 50%', '80% 50%', '65% 50%'),
('乌龟', 'turtle_2026072416', 'Turtle', '🐢', 'turtle.jpg', 'turtle.mp3', '乌龟是地球上最长寿的动物之一，有些陆龟可以活到150岁以上。它们的壳其实是肋骨演化而来。', '50% 50%', '50% 50%', '50% 50%'),
('犀牛', 'rhino_2026072417', 'Rhino', '🦏', 'rhino.jpg', 'rhino.mp3', '犀牛是陆地上仅次于大象的第二大动物。它们的角由角蛋白组成，和人的指甲是同一种物质。', '30% 50%', '50% 50%', '50% 50%'),
('鹰', 'eagle_2026072418', 'Eagle', '🦅', 'eagle.jpg', 'eagle.mp3', '鹰的视力比人类敏锐8倍，能从几公里外看到地面上的小兔子。它们俯冲时速度可超过240公里每小时。', '50% 50%', '50% 50%', '50% 50%'),
('鹦鹉', 'parrot_2026072419', 'Parrot', '🦜', 'parrot.jpg', 'parrot.mp3', '鹦鹉不仅会模仿人说话，还能理解一些词汇的含义。金刚鹦鹉的寿命可达60年以上。', '50% 50%', '50% 50%', '50% 50%'),
('猪', 'pig_2026072420', 'Pig', '🐷', 'pig.jpg', 'pig.mp3', '猪是非常聪明的动物，智商相当于3岁小孩。它们爱干净，会在远离睡觉的地方上厕所。', '40% 50%', '40% 50%', '40% 50%'),
```

### 第三批（12 只）— Code 后缀 `_20260729XX`

新增 12 只动物（蚂蚁、瓢虫、变色龙、蜥蜴、蜻蜓、蜗牛、刺猬、仓鼠、海龟、章鱼、海马、海狮），详见 `ANIMALS.md`。

```
---

## 六、快速模板（需新增动物时直接复制填写）

```python
# ┌─ 第 X 批（2026-07-28）新增 ──────────────────────────
(
    '',                    # 中文名
    '_2026072801',         # code（英文名_日期序号）
    '',                    # English Name
    '',                    # emoji
    '.{ext}',                # 图片文件名（原图格式）
    '.mp3',                # 音频文件名（三目录共用）
    '',                    # 科普知识（40-80 字）
    '% %',                 # image_position（iPhone 竖屏焦点）
    '% %',                 # image_position_ipad_portrait（iPad 竖屏焦点）
    '% %',                 # image_position_ipad_landscape（iPad 横屏焦点）
    '',                    # group（必填: farm/wild/ocean/reptile）
),
```

---

## 七、调试和验证

1. **检查焦点**：运行 `python manage.py runserver`，在浏览器中查看各模式下的图片显示
2. **检查分组**：在浏览模式页面顶部查看 Tabs，确认新动物出现在正确的分组中
3. **检查排序**：确认拼音排序正确（用 `pypinyin`）
4. **确保数量**：练习模式需要至少 4 只动物才能出题；每类分组也建议 ≥ 4 只
5. **音频文件**：确认三个目录都有对应文件，否则播放按钮会变灰色 (`.muted`)

### 验证分组

```python
# 查看每种分组有多少动物
python manage.py shell -c "
from django.db.models import Count
from apps.core.models import Item
for g, cnt in Item.objects.values('group').annotate(c=Count('id')).order_by('group'):
    print(f'{g or \"(无)\"}: {cnt}只')
"

---

## 八、音频生成方式（完整说明）

### 历史背景（为什么要用 edge-tts）

本项目最初的音频方案是 **gTTS（Google Text-to-Speech)**，但实际测试中发现：

| 问题 | 说明 |
|------|------|
| 代理阻断 | 沙箱网络走代理 `127.0.0.1:7890`，gTTS 请求 Google 翻译 API 被代理拦截 |
| 无直连权限 | 不设代理 → DNS 解析失败（沙箱无直连外网权限） |
| 不稳定 | 设代理 → 部分请求能通但极不稳定，批量跑几分钟后随机断开 |
| 环境变量无效 | 尝试 `HTTP_PROXY` / `HTTPS_PROXY` 全部无效 |

因此最终改用 **edge-tts**（Microsoft Edge 内置神经网络语音）。

> ⚠️ **如果你本地能直连 Google（不经过代理），也可以用 gTTS 替代。** 生成命令类似：
> ```python
> from gtts import gTTS
> gTTS('狮子', lang='zh-CN').save('media/audio/lion.mp3')
> gTTS('Lion', lang='en').save('media/audio_en/lion.mp3')
> ```

---

### 当前方案：edge-tts（推荐）

本项目实际使用的是 **edge-tts**（Microsoft Edge 在线 TTS）生成三语发音。

### 8.1 安装 edge-tts

```bash
pip install edge-tts
```

> edge-tts 免费、无需 API Key，在联网环境下直接调用 Edge 的语音合成服务。

### 8.2 可用语音列表

| 用途 | 推荐语音 | 说明 |
|------|---------|------|
| 中文（动物名 + 科普） | `zh-CN-XiaoxiaoNeural` | 女声，自然清晰 |
| 英文（动物名） | `en-US-JennyNeural` | 美式女声 |
| 备选中文 | `zh-CN-YunxiNeural` | 男声，适合科普 |
| 备选中文 | `zh-CN-XiaoyiNeural` | 女声，偏可爱适合幼儿 |

查看所有可用语音：`edge-tts --list-voices`

### 8.3 单只动物的完整生成命令

```bash
# Step 1: 中文发音（只读动物名）
edge-tts --voice zh-CN-XiaoxiaoNeural --text "狮子" --write-media media/audio/lion.mp3

# Step 2: 英文发音（只读动物名）
edge-tts --voice en-US-JennyNeural --text "Lion" --write-media media/audio_en/lion.mp3

# Step 3: 科普发音（全文朗读）
edge-tts --voice zh-CN-XiaoxiaoNeural --text "狮子是唯一群居的猫科动物..." --write-media media/audio_fact/lion.mp3
```

> **⚠️ 三个音频的文件名必须完全一致**，只靠 `media/audio/`、`media/audio_en/`、`media/audio_fact/` 三个目录区分。

### 8.4 批量生成所有动物音频（推荐）

在项目根目录下运行以下脚本，可一次性为 **全部 53 只动物** 重新生成所有音频：

```bash
#!/bin/bash
# 文件：scripts/generate_all_audio.sh（如不存在则创建）
# 用法：bash scripts/generate_all_audio.sh

ANIMALS=(
  "狮子:Lion:狮子是唯一群居的猫科动物，一个狮群通常由1-2头雄狮和几头母狮组成。雄狮的鬃毛越浓密越受母狮青睐。"
  "大象:Elephant:大象是陆地上最大的哺乳动物。它们的鼻子由超过4万块肌肉组成，既能拔起大树也能捡起一粒花生。"
  # ... 按需列出所有动物
)

# 三个目录
DIRS=("media/audio" "media/audio_en" "media/audio_fact")
for d in "${DIRS[@]}"; do
  mkdir -p "$d"
done

for entry in "${ANIMALS[@]}"; do
  IFS=":" read -r zh en fact <<< "$entry"
  # 取拼音或英文名作文件名
  fname="${en,,}"   # 转小写
  fname="${fname// /_}"  # 空格转下划线
  fname="${fname//-/_}"

  # 中文名
  edge-tts --voice zh-CN-XiaoxiaoNeural --text "$zh" --write-media "media/audio/${fname}.mp3"
  # 英文名
  edge-tts --voice en-US-JennyNeural --text "$en" --write-media "media/audio_en/${fname}.mp3"
  # 科普
  edge-tts --voice zh-CN-XiaoxiaoNeural --text "$fact" --write-media "media/audio_fact/${fname}.mp3"

  echo "✅ $zh ($en) → ${fname}.mp3"
done
```

### 8.5 新增动物时快速生成命令（推荐流程）

```bash
# 定义三个变量
ZH_NAME="熊猫"           # 中文动物名（仅动物名，不要加"动物"等后缀）
EN_NAME="Panda"          # 英文动物名
FACT="熊猫是中国国宝，虽然属于食肉目，但99%的食物都是竹子，每天要花12-16小时进食。"  # 科普全文
FILENAME="panda"         # 小写英文文件名（与 seed_data.py 中 img_file 的文件名不含扩展名一致）

# 三连生成
edge-tts --voice zh-CN-XiaoxiaoNeural --text "$ZH_NAME" --write-media "media/audio/${FILENAME}.mp3"
edge-tts --voice en-US-JennyNeural --text "$EN_NAME" --write-media "media/audio_en/${FILENAME}.mp3"
edge-tts --voice zh-CN-XiaoxiaoNeural --text "$FACT" --write-media "media/audio_fact/${FILENAME}.mp3"

echo "✅ $ZH_NAME ($EN_NAME) → ${FILENAME}.mp3 已生成"
```

### 8.6 音频文件检查清单

生成后确认：

```bash
# 检查三个目录都有对应文件
ls -la media/audio/panda.mp3
ls -la media/audio_en/panda.mp3
ls -la media/audio_fact/panda.mp3

# 检查文件是否有内容（大于 1KB 通常正常）
du -sh media/audio/panda.mp3
```

如果某个目录缺少文件，**该语言对应的播放按钮会变灰色**（CSS class `.muted`），不影响其他功能运行，但用户体验打折。

### 8.7 edge-tts 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `No module named edge-tts` | 未安装 | `pip install edge-tts` |
| 网络错误 | 需要访问 `speech.platform.bing.com` | 检查网络/代理 |
| 音频只有几字节 | 网络断开或语音服务不可用 | 重新执行命令 |
| 文件名乱码 | Windows CMD 编码问题 | 在 Git Bash 或 WSL 中执行 |
