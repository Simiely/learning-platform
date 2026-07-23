import glob
import os
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import Category, Item

# Real animal data from word-cards repo
# ---- Animal seed data ----
# image_position 是手动校准的视觉焦点（CSS object-position 格式）。
# 不要用 detect_centers --force 覆盖这些值！
# 修改焦点：直接改下面元组最后一列，然后 seed_data --force。
ANIMALS = [
    # (name, english_name, emoji, img_file, audio_file, fact, image_position)
    ('狮子', 'Lion', '🦁', 'lion.jpg', 'lion.mp3',
     '狮子是唯一群居的猫科动物，一个狮群通常由1-2头雄狮和几头母狮组成。雄狮的鬃毛越浓密越受母狮青睐。',
     '23% 57%'),  # 狮子 — 脸部偏左，手动左移 30%
    ('大象', 'Elephant', '🐘', 'elephant.jpg', 'elephant.mp3',
     '大象是陆地上最大的哺乳动物。它们的鼻子由超过4万块肌肉组成，既能拔起大树也能捡起一粒花生。',
     '58% 83%'),  # 大象 — 手动下移 20%
    ('熊猫', 'Panda', '🐼', 'panda.jpg', 'panda.mp3',
     '大熊猫是中国国宝，虽然属于食肉目，但99%的食物都是竹子，每天要花12-16小时进食。',
     '46% 55%'),
    ('老虎', 'Tiger', '🐯', 'tiger.jpg', 'tiger.mp3',
     '老虎是世界上最大的猫科动物，每只老虎身上的条纹都是独一无二的，就像人类的指纹一样。',
     '52% 54%'),
    ('长颈鹿', 'Giraffe', '🦒', 'giraffe.jpg', 'giraffe.mp3',
     '长颈鹿是地球上最高的陆地动物，脖子虽然很长，但颈椎骨数量和人类一样都是7块。',
     '49% 35%'),  # 长颈鹿 — 手动上移 40%
    ('斑马', 'Zebra', '🦓', 'zebra.jpg', 'zebra.mp3',
     '斑马的黑白条纹不仅是伪装，还能防蚊虫叮咬。每只斑马的条纹图案都是独一无二的。',
     '62% 73%'),  # 斑马 — 手动右移 10%
    ('企鹅', 'Penguin', '🐧', 'penguin.jpg', 'penguin.mp3',
     '企鹅是鸟类中的游泳高手，帝企鹅可以潜入500米深的海水中，憋气超过20分钟。',
     '46% 45%'),  # 企鹅 — 手动上移 20%
    ('海豚', 'Dolphin', '🐬', 'dolphin.jpg', 'dolphin.mp3',
     '海豚是非常聪明的海洋哺乳动物，它们用超声波定位和交流，睡觉时大脑一半休息一半保持清醒。',
     '42% 70%'),
    ('猴子', 'Monkey', '🐵', 'monkey.jpg', 'monkey.mp3',
     '猴子是灵长类动物中种类最丰富的一类，它们有复杂的社会结构，会使用工具和互相梳理毛发。',
     '45% 72%'),  # 猴子 — 手动下移 20%
    ('兔子', 'Rabbit', '🐰', 'rabbit.jpg', 'rabbit.mp3',
     '兔子的耳朵可以转动270度，帮助它们听到远处的危险。它们高兴时会跳起来在空中转身，这叫binky。',
     '45% 63%'),
    ('猫', 'Cat', '🐱', 'cat.jpg', 'cat.mp3',
     '猫是世界上最受欢迎的宠物之一。它们的胡须能感知空气的细微变化，帮助它们在黑暗中判断方向。',
     '56% 38%'),
    ('狗', 'Dog', '🐶', 'dog.jpg', 'dog.mp3',
     '狗是人类最早驯化的动物，它们的嗅觉比人类灵敏1万到10万倍，能嗅出疾病和情绪变化。',
     '49% 69%'),
    ('马', 'Horse', '🐴', 'horse.jpg', 'horse.mp3',
     '马可以站着睡觉，但需要躺下才能进入深度睡眠。它们的视野差不多达到360度。',
     '59% 66%'),  # 马 — 手动右移 10%
    ('牛', 'Cow', '🐮', 'cow.jpg', 'cow.mp3',
     '牛有四个胃室来消化草料，它们能看到颜色，而且对红色其实并不敏感。',
     '38% 64%'),  # 牛 — 手动左移 20%
    ('羊', 'Sheep', '🐑', 'sheep.jpg', 'sheep.mp3',
     '绵羊有极好的记忆力，能记住50多张面孔长达两年。它们还能通过面部表情识别同伴的情绪。',
     '48% 60%'),
    ('鸡', 'Chicken', '🐔', 'chicken.jpg', 'chicken.mp3',
     '鸡是世界上最常见的鸟类，全球养殖数量超过250亿只。它们能用超过30种不同的叫声来交流。',
     '54% 16%'),  # 鸡 — 手动上移 45%
    ('鸭子', 'Duck', '🦆', 'duck.jpg', 'duck.mp3',
     '鸭子的脚掌不会感到冷，因为它们脚上的血管排列特殊，能回收热量。小鸭子会把出生后看到的第一个移动物体当妈妈。',
     '32% 81%'),  # 鸭子 — 更换为 pexels-didsss-33312410-2.jpg
    ('鱼', 'Fish', '🐟', 'fish.jpg', 'fish.mp3',
     '鱼类是地球上最古老的脊椎动物，已经存在超过5亿年。有些鱼能改变性别，有些能发电。',
     '87% 44%'),  # 鱼 — 手动右移 30%
    ('蝴蝶', 'Butterfly', '🦋', 'butterfly.jpg', 'butterfly.mp3',
     '蝴蝶用脚来尝味道！它们的翅膀上覆盖着细小的鳞片，这些鳞片能反射光线产生绚丽的色彩。',
     '54% 56%'),
    ('青蛙', 'Frog', '🐸', 'frog.jpg', 'frog.mp3',
     '青蛙的皮肤可以吸收水分和氧气，所以它们对环境污染特别敏感。它们是环境健康的"指示物种"。',
     '53% 56%'),  # 青蛙 — 手动右移 5%
    ('鲨鱼', 'Shark', '🦈', 'shark.jpg', 'shark.mp3',
     '鲨鱼比恐龙出现的时间还早，已经在地球上生存超过4亿年。它们一生会换掉超过3万颗牙齿。',
     '95% 50%'),  # 鲨鱼 — 手动右移 40%
]


def _write_media_file(rel_path, content_bytes):
    """Write bytes to MEDIA_ROOT/rel_path deterministically.

    Django's FileField.save() appends a random `_<suffix>` when the target
    name already exists on disk (e.g. re-running seed_data over the committed
    media files). That desyncs the DB filename from the canonical file and
    causes 404s. This helper overwrites the canonical plain name instead and
    removes any leftover suffixed orphans, so the stored name always equals
    rel_path and survives a fresh clone + migrate + seed_data anywhere.
    """
    from django.conf import settings
    base_dir, fname = os.path.split(rel_path)
    stem, dot, ext = fname.rpartition(".")
    full_dir = os.path.join(settings.MEDIA_ROOT, base_dir)
    os.makedirs(full_dir, exist_ok=True)
    if stem and ext:
        for old in glob.glob(os.path.join(full_dir, f'{stem}_*.{ext}')):
            try:
                os.remove(old)
            except OSError:
                pass
    dest = os.path.join(full_dir, fname)
    with open(dest, 'wb') as fh:
        fh.write(content_bytes)
    return rel_path.replace('\\', '/')


class Command(BaseCommand):
    help = "Seed the database with sample categories and items"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing data without confirmation",
        )

    def handle(self, *args, **options):
        MEDIA_ROOT = settings.MEDIA_ROOT

        if Category.objects.exists() and not options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    "Data already exists. Use --force to overwrite, "
                    "or delete existing data first."
                )
            )
            return

        Item.objects.all().delete()
        Category.objects.all().delete()

        categories_data = [
            ('动物', 'animals', '认识各种动物', 1, '🐾'),
        ]

        cat_objs = {}
        for name, slug, desc, order, icon in categories_data:
            cat = Category.objects.create(
                name=name, slug=slug,
                icon=icon,
                description=desc, sort_order=order
            )
            cat_objs[slug] = cat
            self.stdout.write(f'  Created category: {name}')

        items_data = [
            ('animals', ANIMALS, True),
        ]

        for slug, items, use_real_media in items_data:
            cat = cat_objs[slug]
            for idx, (name, en_name, emoji, img_file, audio_file, fact, img_pos) in enumerate(items):
                item = Item.objects.create(
                    category=cat,
                    name=name,
                    english_name=en_name,
                    emoji=emoji,
                    fact=fact,
                    image_position=img_pos or "50% 50%",
                    image_position_checked=True,
                    sort_order=idx,
                )

                if use_real_media:
                    # Image — write canonical plain name (no Django `_<suffix>`)
                    if img_file:
                        src = os.path.join(MEDIA_ROOT, 'images', img_file)
                        if os.path.exists(src):
                            with open(src, 'rb') as f:
                                item.image = _write_media_file(os.path.join('images', img_file), f.read())
                            item.save(update_fields=['image'])
                    # Audio zh / en / fact — same canonical-name treatment
                    if audio_file:
                        for sub, field in (('audio', 'audio'), ('audio_en', 'audio_en'), ('audio_fact', 'audio_fact')):
                            src = os.path.join(MEDIA_ROOT, sub, audio_file)
                            if os.path.exists(src):
                                with open(src, 'rb') as f:
                                    setattr(item, field, _write_media_file(os.path.join(sub, audio_file), f.read()))
                        item.save(update_fields=["audio", "audio_en", "audio_fact"])
                self.stdout.write(f'    {cat.name}: {name}')

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
