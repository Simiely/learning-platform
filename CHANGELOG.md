# CHANGELOG.md · 版本记录

> 项目无正式版本 tag，按开发里程碑从新到旧。完整问题记录见 [DEV.md](DEV.md)。

## 最新里程碑（2026-07-31 大版本）

- **模块化重构**：CSS 巨石 1174 行拆为 13 模块按需加载；JS 抽取 4 个共享模块（audio-player / image-zoom / ipad-detect / confetti）+ 页面级独立 JS（browse / cards / quiz）；模板只保留 `xxxApp({...})` 初始化
- **数据源重构**：seed_data.py 元组 → `apps/core/data/` 目录（CardItem dataclass + 每分类一个文件），7 分类 183 条目
- **浏览分组 Tabs**：按生活场景零交叉分组（家里和农场/野生动物/海洋动物/爬虫和昆虫），手机窄屏默认只显 emoji
- **字母区块模式**：拼音（🀄）/英文（🔤）互斥区块切换，点击再点取消，与分组过滤互不干扰
- **图片 >4MB 压缩**：mozjpeg 压缩到 4MB 内不降分辨率（15 张 88.2MB→51.4MB），Windows 坑已记录

## 功能演进

- **7 分类内容扩充**：动物 77 / 果蔬 23 / 交通 20 / 恐龙 16 / 太空 15 / 花卉 16 / 职业 16
- **三套图片焦点**：iPhone 竖 / iPad 竖 / iPad 横（迁移 0011），前端 `screen.width>=768` + 方向检测
- **seed_sync 增量同步**（2026-07-25）：`code` 稳定唯一键 + `update_or_create`，Docker 部署不丢用户数据
- **双模式存储升级**：本地 + 云端（Docker 部署）；安全加固（open redirect 校验、DEBUG 默认 False、登出改 POST）
- **edge-tts 音频**（2026-07-24）：gTTS 被代理拦截 → edge-tts（Azure 流，代理友好），中文/英文/科普三套

## 稳定化修复（2026-07-23 ~ 07-26 集中迭代）

- iOS Safari：100vh+bfcache 铺满失效 → JS `--vh`；flex+min-height 塌缩 → 回退；刘海 safe-area 避让
- Alpine.js CDN 被 Tracking Prevention 拦截 → 本地托管
- IIFE 缺分号致全部 JS 崩溃 → 修复 + 教训
- 练习模式音频串音 → 题目数据冻结 + 序列 ID 防护
- Canvas 礼花 iPad 卡顿 → devicePixelRatio 适配
- N+1 查询修复、view_count 启动 bug（get_or_create created 返回值）
- Quiz 出题去重物理限制 → 正确答案互不重复 + 干扰项允许复用

## 初始版本

- Django + Alpine.js 幼儿闪卡平台：浏览/卡片/练习三模式，触屏适配，中英双语发音
