# TODO — 动物闪卡平台后续工作

> 本文件用于跨设备 / 跨 AI 会话接力。代码、迁移、媒体素材、文档均已推送至 `master`，
> 换电脑 `git clone` 即可获得完整可运行状态。下面是需要**继续推进**的事项和**已定决策**。

## 一、待做清单

### A. 服务器实际部署（核心，尚未真做）
代码已上库，但 `db.sqlite3` 故意不入库（见 `.gitignore`）。部署时靠种子脚本确定性重建数据：
```bash
pip install -r requirements.txt
python manage.py migrate            # 应用迁移 0012，建立 Item.group 字段
python manage.py seed_data --force  # 确定性重建 61 只动物 + 媒体关联（不依赖本地库）
python manage.py collectstatic      # 用 gunicorn 生产部署时需要
```
执行后状态 = 本地当前状态（61 只、4 分组、每张图 + 3 段语音齐全）。

### B. ALLOWED_HOSTS 补域名 ⚠️
`config/settings.py` 目前只含 `127.0.0.1`。部署到真实服务器前，必须通过环境变量或配置把
服务器域名 / IP 加入 `ALLOWED_HOSTS`，否则 Django 拒访。

### C. 图片焦点校准
第3~5批 31 只动物目前已校准焦点。如需微调，改
`apps/core/management/commands/seed_data.py` 对应元组的焦点值，再跑 `python manage.py sync_positions`。
焦点约定见 `DEVELOPER.md`。

### D. 后续动物批次
- **中优先级 8 种**：✅ **已全部上线**（第4批梅花鹿 + 第5批棕熊/大猩猩/孔雀/火烈鸟/天鹅/萤火虫/蜘蛛）。
- **精选 6 种**：水母、海星、蝙蝠、树懒、水獭、老鼠，待规划。
- 音频生成工具 `gen_audio.py`（仓库根目录）可直接复用：在 ANIMALS 列表追加
  `(base, 中文名, 英文名, 科普文案)`，运行 `python gen_audio.py` 即可。
- 图片下载工具 `download_unsplash.py`（仓库根目录）用于获取候选参考图。

### E. 本地预览服务（验证完可停）
开发期后台 dev server 在 `http://127.0.0.1:8000`，确认效果后可停止。

## 二、已定决策（无需再问，直接照做）

1. **Emoji 规则**：动物有专属 emoji 用自己；没有的，用其**所属分组的图标**。
   - 分组图标：家里和农场 🏠 / 野生动物 🌍 / 海洋动物 🌊 / 爬虫和昆虫 🦎
   - 实例：蜻蜓（无专属）→ 🦎；海马（无专属）→ 🌊；变色龙/蜥蜴（无专属）→ 🦎
   - 有专属 emoji 的维持不变：蚂蚁🐜、瓢虫🐞、蜗牛🐌、刺猬🦔、仓鼠🐹、海龟🐢、章鱼🐙、海狮🦭 等。
2. **图片不裁正方形**：`media/images/` 现有图均为长方形，App 用 `object-fit: cover` + 焦点适配。
   高清图原样搬入即可（长边 ≥ 3000px）。
3. **媒体文件命名**：图片/音频用简单英文名做基名（如 `ant.jpg` / `ant.mp3`），
   须与 `seed_data.py` 中该动物的 `img_file` / `audio_file` 基名一致。
4. **批次结构**：第1批+第2批共 41 只已上线；第3批 12 只已上线（详见 `ANIMALS.md`）。
5. **依赖版本**：`requirements.txt` 已统一为本地运行环境版本（Django 6.0.7 等），部署照此安装。

## 三、需要你（用户）提供的密钥 / 凭据

以下密钥**刻意不入库**（安全），新环境需由用户提供给 AI：

| 用途 | 名称 | 说明 |
|------|------|------|
| 参考图搜索 | Unsplash Access Key | `download_unsplash.py` 调用 Unsplash API 搜图 |
| 参考图搜索 | Pexels API Key | 备用图源（Pexels API 搜图 + CDN 下载） |
| 代码仓库 | GitHub PAT | 推送到 `Simiely/learning-platform` 用；推送 URL 格式为
  `https://x-access-token:<PAT>@github.com/...`（用户名固定 `x-access-token`） |

> 音频生成用 edge-tts（微软免费服务），**无需密钥**，但所在环境需能访问外网（必要时走代理）。

## 四、跨设备接力提示

- 本仓库**不含** `db.sqlite3`、`venv/`、本地 `new-animals/` 临时目录、用户级记忆里的密钥。
- `gen_audio.py` 与 `download_unsplash.py` 已入库，换电脑可直接调用。
- 若推送时遇 `github.com:443` 超时：多为 git 代理配置问题，确认代理可用后
  用 `git -c http.https://github.com.proxy=<代理地址> push ...` 显式指定。
