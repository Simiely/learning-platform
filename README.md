# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django + Alpine.js** 的幼儿识字/认知闪卡平台，支持 **浏览、卡片、练习** 三种学习模式，专为触屏（iPad / iPhone）设计。内置 **53 种动物**（分 4 组）的中英文对照学习，配三语自动发音。

## 快速开始

```bash
git clone https://github.com/Simiely/learning-platform.git
cd learning-platform
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate && python manage.py seed_data
python manage.py runserver 0.0.0.0:8000
```

打开 **http://localhost:8000** 即可使用。

---

## 你是哪种角色？

### 👶 想直接使用？
三种学习模式：
- **浏览** `/category/animals/` — 方块网格，点击弹窗详情+发音
- **卡片** `/category/animals/cards/` — 全屏翻卡，随机起始，自动发音
- **练习** `/category/animals/quiz/` — 看图选词，10 题一组，答对撒花

点击文字行或喇叭图标播放对应语音，右上角切换深色/浅色/跟随系统主题。

### 🐣 想新加一种动物？
看操作手册 → **[`ADD_ANIMALS_GUIDE.md`](./ADD_ANIMALS_GUIDE.md)**

包含：图片素材下载 → 音频生成（edge-tts）→ 数据整合 → 入库完整流程。

### 🧑‍💻 想开发或改代码？
看开发者文档 → **[`DEVELOPER.md`](./DEVELOPER.md)**

包含：技术栈、项目结构、数据模型、路由、修改规则、前端架构、常见问题排查、Docker 部署。

### 🐛 遇到了奇怪的问题？
看踩坑记录 → **[`DEV.md`](./DEV.md)**

包含：Safari 适配、图片焦点、音频播放、CSS 布局等全部历史问题与解决方案。

### 📋 想知道接下来做什么？
看待办清单 → **[`TODO.md`](./TODO.md)**

---

## License

MIT
