import os
import shutil
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from apps.core.models import Category, Item

COLORS = {
    'animals': ('#b8860b', '#3c2d12'),
    'numbers': ('#4a7c59', '#2d3a1e'),
    'words': ('#4a7c59', '#2d3a1e'),
    'sports': ('#c0392b', '#4a1515'),
}

# Real animal data from word-cards repo
# Real animal data from word-cards repo
ANIMALS = [
    ('狮子', 'Lion', '🦁', 'lion.jpg', 'lion.mp3', '狮子是唯一群居的猫科动物，一个狮群通常由1-2头雄狮和几头母狮组成。雄狮的鬃毛越浓密越受母狮青睐。'),
    ('大象', 'Elephant', '🐘', 'elephant.jpg', 'elephant.mp3', '大象是陆地上最大的哺乳动物。它们的鼻子由超过4万块肌肉组成，既能拔起大树也能捡起一粒花生。'),
    ('熊猫', 'Panda', '🐼', 'panda.jpg', 'panda.mp3', '大熊猫是中国国宝，虽然属于食肉目，但99%的食物都是竹子，每天要花12-16小时进食。'),
    ('老虎', 'Tiger', '🐯', 'tiger.jpg', 'tiger.mp3', '老虎是世界上最大的猫科动物，每只老虎身上的条纹都是独一无二的，就像人类的指纹一样。'),
    ('长颈鹿', 'Giraffe', '🦒', 'giraffe.jpg', 'giraffe.mp3', '长颈鹿是地球上最高的陆地动物，脖子虽然很长，但颈椎骨数量和人类一样都是7块。'),
    ('斑马', 'Zebra', '🦓', 'zebra.jpg', 'zebra.mp3', '斑马的黑白条纹不仅是伪装，还能防蚊虫叮咬。每只斑马的条纹图案都是独一无二的。'),
    ('企鹅', 'Penguin', '🐧', 'penguin.jpg', 'penguin.mp3', '企鹅是鸟类中的游泳高手，帝企鹅可以潜入500米深的海水中，憋气超过20分钟。'),
    ('海豚', 'Dolphin', '🐬', 'dolphin.jpg', 'dolphin.mp3', '海豚是非常聪明的海洋哺乳动物，它们用超声波定位和交流，睡觉时大脑一半休息一半保持清醒。'),
    ('猴子', 'Monkey', '🐵', 'monkey.jpg', 'monkey.mp3', '猴子是灵长类动物中种类最丰富的一类，它们有复杂的社会结构，会使用工具和互相梳理毛发。'),
    ('兔子', 'Rabbit', '🐰', 'rabbit.jpg', 'rabbit.mp3', '兔子的耳朵可以转动270度，帮助它们听到远处的危险。它们高兴时会跳起来在空中转身，这叫binky。'),
    ('猫', 'Cat', '🐱', 'cat.jpg', 'cat.mp3', '猫是世界上最受欢迎的宠物之一。它们的胡须能感知空气的细微变化，帮助它们在黑暗中判断方向。'),
    ('狗', 'Dog', '🐶', 'dog.jpg', 'dog.mp3', '狗是人类最早驯化的动物，它们的嗅觉比人类灵敏1万到10万倍，能嗅出疾病和情绪变化。'),
    ('马', 'Horse', '🐴', 'horse.jpg', 'horse.mp3', '马可以站着睡觉，但需要躺下才能进入深度睡眠。它们的视野差不多达到360度。'),
    ('牛', 'Cow', '🐮', 'cow.jpg', 'cow.mp3', '牛有四个胃室来消化草料，它们能看到颜色，而且对红色其实并不敏感。'),
    ('羊', 'Sheep', '🐑', 'sheep.jpg', 'sheep.mp3', '绵羊有极好的记忆力，能记住50多张面孔长达两年。它们还能通过面部表情识别同伴的情绪。'),
    ('鸡', 'Chicken', '🐔', 'chicken.jpg', 'chicken.mp3', '鸡是世界上最常见的鸟类，全球养殖数量超过250亿只。它们能用超过30种不同的叫声来交流。'),
    ('鸭子', 'Duck', '🦆', 'duck.jpg', 'duck.mp3', '鸭子的脚掌不会感到冷，因为它们脚上的血管排列特殊，能回收热量。小鸭子会把出生后看到的第一个移动物体当妈妈。'),
    ('鱼', 'Fish', '🐟', 'fish.jpg', 'fish.mp3', '鱼类是地球上最古老的脊椎动物，已经存在超过5亿年。有些鱼能改变性别，有些能发电。'),
    ('蝴蝶', 'Butterfly', '🦋', 'butterfly.jpg', 'butterfly.mp3', '蝴蝶用脚来尝味道！它们的翅膀上覆盖着细小的鳞片，这些鳞片能反射光线产生绚丽的色彩。'),
    ('青蛙', 'Frog', '🐸', 'frog.jpg', 'frog.mp3', '青蛙的皮肤可以吸收水分和氧气，所以它们对环境污染特别敏感。它们是环境健康的"指示物种"。'),
    ('鲨鱼', 'Shark', '🦈', 'shark.jpg', 'shark.mp3', '鲨鱼比恐龙出现的时间还早，已经在地球上生存超过4亿年。它们一生会换掉超过3万颗牙齿。'),
]

# Simplified data for other categories
NUMBERS = [
    ('1', 'One', '1', '', '', '数字 1 是所有计数的开始。'),
    ('2', 'Two', '2', '', '', '数字 2 表示一双，比如一双鞋、一双手。'),
    ('3', 'Three', '3', '', '', '数字 3 是三角形的基本数量。'),
    ('4', 'Four', '4', '', '', '数字 4 像一个板凳的四条腿。'),
    ('5', 'Five', '5', '', '', '数字 5 像一只手有五根手指。'),
    ('6', 'Six', '6', '', '', '数字 6 倒过来看就像数字 9。'),
    ('7', 'Seven', '7', '', '', '数字 7 在彩虹中有七种颜色。'),
    ('8', 'Eight', '8', '', '', '数字 8 横着看就是无限符号。'),
    ('9', 'Nine', '9', '', '', '数字 9 是最大的个位数。'),
    ('10', 'Ten', '10', '', '', '数字 10 是我们最常用的进制基础。'),
]

WORDS = [
    ('苹果', 'Apple', '🍎', '', '', '苹果是一种常见的水果，又红又圆，吃起来又脆又甜。'),
    ('书本', 'Book', '📖', '', '', '书本里藏着很多知识和故事，是人类进步的阶梯。'),
    ('太阳', 'Sun', '☀', '', '', '太阳是一颗恒星，给地球带来光和热，万物生长靠太阳。'),
    ('月亮', 'Moon', '🌙', '', '', '月亮是地球的卫星，每个月从弯弯的月牙变成圆圆的满月。'),
    ('星星', 'Star', '⭐', '', '', '星星在夜空中一闪一闪的，每一颗都可能比太阳还要大。'),
    ('大树', 'Tree', '🌳', '', '', '大树可以活几百年甚至上千年，是地球的绿色守护者。'),
    ('房子', 'House', '🏠', '', '', '房子为我们遮风挡雨，是每个人温暖的家。'),
    ('汽车', 'Car', '🚗', '', '', '汽车是我们最常见的交通工具，用四个轮子在路上跑。'),
    ('花朵', 'Flower', '🌸', '', '', '花朵有各种各样的颜色和形状，蜜蜂最喜欢在花丛中采蜜。'),
    ('彩虹', 'Rainbow', '🌈', '', '', '雨过天晴时天空中会出现七色彩虹，红橙黄绿青蓝紫。'),
    ('云朵', 'Cloud', '☁', '', '', '云朵飘在天空中，有的时候像棉花糖，有的时候像小动物。'),
    ('高山', 'Mountain', '⛰', '', '', '高山巍峨壮观，世界最高峰珠穆朗玛峰有八千多米高。'),
]

SPORTS = [
    ('足球', 'Football', '⚽', '', '', '足球是世界上最多人参与的运动，用脚踢球射门得分。'),
    ('篮球', 'Basketball', '🏀', '', '', '篮球是五个人的团队运动，把球投进篮筐就能得分。'),
    ('游泳', 'Swimming', '🏊', '', '', '游泳是在水中的运动，蛙泳、自由泳、仰泳和蝶泳是四种基本泳姿。'),
    ('跑步', 'Running', '🏃', '', '', '跑步是最简单的运动，每天坚持跑步可以让身体更健康。'),
    ('网球', 'Tennis', '🎾', '', '', '网球用球拍击球过网，可以一个人打也可以两个人对打。'),
    ('骑车', 'Cycling', '🚴', '', '', '骑自行车既能锻炼身体又能环保出行。'),
    ('滑雪', 'Skiing', '⛷', '', '', '滑雪是冬天的运动，踩在雪板上从雪山上滑下来，非常刺激。'),
    ('棒球', 'Baseball', '⚾', '', '', '棒球用球棒击球然后跑垒得分，在美国和日本非常受欢迎。'),
    ('排球', 'Volleyball', '🏐', '', '', '排球是六个人的团队运动，用手把球打过网，不能落地。'),
    ('体操', 'Gymnastics', '🤸', '', '', '体操运动员的身体非常灵活，能做出翻跟斗、转圈等高难度动作。'),
]

MEDIA_DIR = None


def _get_chinese_font(size):
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simsun.ttc',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except (OSError, IOError):
                continue
    try:
        return ImageFont.truetype('arial.ttf', size)
    except (OSError, IOError):
        return ImageFont.load_default()


def generate_placeholder_image(text, bg_color, text_color, size=(300, 300)):
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    font = _get_chinese_font(50)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - tw) / 2
    y = (size[1] - th) / 2
    draw.text((x, y), text, fill=text_color, font=font)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = 'Seed the database with sample categories and items'

    def handle(self, *args, **options):
        global MEDIA_DIR
        from django.conf import settings
        MEDIA_DIR = settings.MEDIA_ROOT

        Item.objects.all().delete()
        Category.objects.all().delete()

        categories_data = [
            ('动物', 'animals', '认识各种动物', 1, '🐾'),
            ('数字', 'numbers', '学习数字 1-10', 2, '🔢'),
            ('词语', 'words', '常用日常词语', 3, '📖'),
            ('运动', 'sports', '认识体育运动', 4, '⚽'),
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
            ('numbers', NUMBERS, False),
            ('words', WORDS, False),
            ('sports', SPORTS, False),
        ]

        for slug, items, use_real_media in items_data:
            cat = cat_objs[slug]
            for idx, (name, en_name, emoji, img_file, audio_file, fact) in enumerate(items):
                item = Item.objects.create(
                    category=cat,
                    name=name,
                    english_name=en_name,
                    emoji=emoji,
                    fact=fact,
                    sort_order=idx,
                )

                if use_real_media:
                    # Image
                    if img_file:
                        src = os.path.join(MEDIA_DIR, 'images', img_file)
                        if os.path.exists(src):
                            with open(src, 'rb') as f:
                                item.image.save(img_file, ContentFile(f.read()))
                            # Compute bg color from saved image
                            from apps.core.views import _image_bg_color
                            item.bg_color = _image_bg_color(item.image.path) or ''
                    # Audio zh / en / fact
                    if audio_file:
                        src = os.path.join(MEDIA_DIR, 'audio', audio_file)
                        if os.path.exists(src):
                            with open(src, 'rb') as f:
                                item.audio.save(audio_file, ContentFile(f.read()))
                        src_en = os.path.join(MEDIA_DIR, 'audio_en', audio_file)
                        if os.path.exists(src_en):
                            with open(src_en, 'rb') as f:
                                item.audio_en.save(audio_file, ContentFile(f.read()))
                        src_fact = os.path.join(MEDIA_DIR, 'audio_fact', audio_file)
                        if os.path.exists(src_fact):
                            with open(src_fact, 'rb') as f:
                                item.audio_fact.save(audio_file, ContentFile(f.read()))
                else:
                    bg, fg = COLORS.get(slug, ('#888', '#fff'))
                    placeholder = generate_placeholder_image(name, bg, fg)
                    item.image.save(f'{slug}_{idx}.png', placeholder)

                self.stdout.write(f'    {cat.name}: {name}')

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
