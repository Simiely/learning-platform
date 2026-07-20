# 项目交接文档

## 基本信息

| 项目 | Lets Learn |
|------|-----------|
| 仓库 | https://github.com/Simiely/learning-platform |
| 分支 | master |
| 技术栈 | Django 5.x + Alpine.js + SQLite/PostgreSQL |
| Python | 3.13+ |
| 本地地址 | http://localhost:8000 |

## 环境启动

```bash
# 1. 克隆
git clone https://github.com/Simiely/learning-platform.git
cd learning-platform

# 2. 虚拟环境
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. 依赖
pip install -r requirements.txt

# 4. 数据库
python manage.py migrate
python manage.py seed_data     # 加载示例动物数据

# 5. 创建管理员（可选）
python manage.py createsuperuser

# 6. 启动
python manage.py runserver
```

## 核心逻辑文件

| 文件 | 作用 |
|------|------|
| `apps/core/models.py` | 数据模型：Category, Item, LearningProgress, QuizAttempt |
| `apps/core/views.py` | 全部视图 + emoji取色 + 图片平均色计算 |
| `apps/core/management/commands/seed_data.py` | 种子数据加载 |
| `templates/category_browse.html` | 浏览模式（网格 + 弹窗） |
| `templates/category_cards.html` | 卡片模式（全屏沉浸） |
| `templates/category_quiz.html` | 练习模式（看图选词） |
| `templates/browse_popup.html` | 浏览弹窗（含 `showPopup` 函数） |
| `static/css/style.css` | 全局样式（CSS Variables + flex布局） |

## 数据模型关键字段

### Category
- `name` — 分类名（如"动物"）
- `slug` — URL slug
- `icon` — emoji 图标
- `item_count` — 自动计算的项数

### Item
- `name` — 中文名
- `english_name` — 英文名
- `emoji` — emoji 字符
- `fact` — 科普文字
- `image` — 图片文件
- `bg_color` — 图片平均色+60%黑（自动计算）
- `audio` — 中文语音
- `audio_en` — 英文语音
- `audio_fact` — 科普语音

## 添加新内容流程

1. 准备素材放在 `media/` 对应目录（images, audio, audio_en, audio_fact）
2. 编辑 `seed_data.py`，按现有格式添加数据
3. 运行 `python manage.py seed_data`
4. `bg_color` 自动计算，emoji 取色自动

## 已知注意事项

1. **Windows emoji 渲染**：`_emoji_color` 依赖 `C:/Windows/Fonts/seguiemj.ttf`，Linux 部署需要安装对应 emoji 字体
2. **pypinyin**：需要单独安装 `pip install pypinyin`
3. **numpy**：图片平均色计算依赖 `numpy`
4. **flex 布局**：整个页面使用嵌套 flex 链，修改布局时务必注意 `min-height:0` 规则
5. **音频文件**：三种音频在 `items_json` 和 `item_detail_api` 两处都要更新
6. **CSS Variables**：颜色系统定义在 `style.css` 的 `:root` 中

## 常见问题排查

| 症状 | 根因 | 解决 |
|------|------|------|
| 练习模式 layout 跳动 | `x-if` 条件渲染导致高度变化 | 改用 `x-show` + 固定 height |
| 英文/科普音频不播放 | `item_detail_api` 未传 `audio_en/fact` | 同步更新两处 JSON |
| 卡片翻页按钮不响应 | 闭包变量丢失 | 用 `window.cardItems` 全局 |
| 图片留白区域无色 | `bg_color` 为空 | 重新 seed 或用 admin 手动设值 |
| 浏览模式排序错乱 | 未按拼音排序 | 检查 `pypinyin` 是否安装 |

## 后续规划建议

- [ ] 添加更多分类（水果、交通工具、颜色……）
- [ ] 增加语音跟读评分功能
- [ ] 家长守护页面（学习报告）
- [ ] 移动端 PWA 离线支持
- [ ] 多语言切换
- [ ] CDN 加速媒体文件
