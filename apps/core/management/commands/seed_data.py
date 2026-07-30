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
# 每只动物 11 个字段: (name, code, english_name, emoji, img_file, audio_file,
#                       fact, image_position, image_position_ipad_portrait,
#                       image_position_ipad_landscape, group)
ANIMALS = [
    # ====== 第一批（2026-07-23）21 只 ======
    # ── 🏠 家里和农场 ──
    ('狗', 'dog_2026072312', 'Dog', '🐶', 'dog.jpg', 'dog.mp3',
     '狗是人类最早驯化的动物，它们的嗅觉比人类灵敏1万到10万倍，能嗅出疾病和情绪变化。',
     '49% 29%', '49% 29%', '49% 29%', 'farm'),
    ('猫', 'cat_2026072311', 'Cat', '🐱', 'cat.jpg', 'cat.mp3',
     '猫是世界上最受欢迎的宠物之一。它们的胡须能感知空气的细微变化，帮助它们在黑暗中判断方向。',
     '56% 28%', '56% 28%', '56% 38%', 'farm'),
    ('兔子', 'rabbit_2026072310', 'Rabbit', '🐰', 'rabbit.jpg', 'rabbit.mp3',
     '兔子的耳朵可以转动270度，帮助它们听到远处的危险。它们高兴时会跳起来在空中转身，这叫binky。',
     '45% 23%', '45% 23%', '45% 23%', 'farm'),
    ('马', 'horse_2026072313', 'Horse', '🐴', 'horse.jpg', 'horse.mp3',
     '马可以站着睡觉，但需要躺下才能进入深度睡眠。它们的视野差不多达到360度。',
     '59% 66%', '44% 66%', '49% 66%', 'farm'),
    ('牛', 'cow_2026072314', 'Cow', '🐮', 'cow.jpg', 'cow.mp3',
     '牛有四个胃室来消化草料，它们能看到颜色，而且对红色其实并不敏感。',
     '28% 54%', '38% 54%', '38% 54%', 'farm'),
    ('羊', 'sheep_2026072315', 'Sheep', '🐑', 'sheep.jpg', 'sheep.mp3',
     '绵羊有极好的记忆力，能记住50多张面孔长达两年。它们还能通过面部表情识别同伴的情绪。',
     '48% 60%', '48% 60%', '48% 60%', 'farm'),
    ('鸡', 'chicken_2026072316', 'Chicken', '🐔', 'chicken.jpg', 'chicken.mp3',
     '鸡是世界上最常见的鸟类，全球养殖数量超过250亿只。它们能用超过30种不同的叫声来交流。',
     '54% 6%', '54% 6%', '54% 6%', 'farm'),
    ('鸭子', 'duck_2026072317', 'Duck', '🦆', 'duck.jpg', 'duck.mp3',
     '鸭子的脚掌不会感到冷，因为它们脚上的血管排列特殊，能回收热量。小鸭子会把出生后看到的第一个移动物体当妈妈。',
     '32% 71%', '32% 71%', '32% 78%', 'farm'),
    ('猪', 'pig_2026072420', 'Pig', '🐷', 'pig.jpg', 'pig.mp3',
     '猪是非常聪明的动物，智商相当于3岁小孩。它们爱干净，会在远离睡觉的地方上厕所。',
     '40% 50%', '40% 50%', '40% 50%', 'farm'),

    # ── 🌍 野生动物 ──
    ('狮子', 'lion_2026072301', 'Lion', '🦁', 'lion.jpg', 'lion.mp3',
     '狮子是唯一群居的猫科动物，一个狮群通常由1-2头雄狮和几头母狮组成。雄狮的鬃毛越浓密越受母狮青睐。',
     '13% 47%', '23% 37%', '23% 47%', 'wild'),
    ('大象', 'elephant_2026072302', 'Elephant', '🐘', 'elephant.jpg', 'elephant.mp3',
     '大象是陆地上最大的哺乳动物。它们的鼻子由超过4万块肌肉组成，既能拔起大树也能捡起一粒花生。',
     '78% 63%', '58% 63%', '58% 53%', 'wild'),
    ('熊猫', 'panda_2026072303', 'Panda', '🐼', 'panda.jpg', 'panda.mp3',
     '大熊猫是中国国宝，虽然属于食肉目，但99%的食物都是竹子，每天要花12-16小时进食。',
     '46% 25%', '46% 25%', '46% 32%', 'wild'),
    ('老虎', 'tiger_2026072304', 'Tiger', '🐯', 'tiger.jpg', 'tiger.mp3',
     '老虎是世界上最大的猫科动物，每只老虎身上的条纹都是独一无二的，就像人类的指纹一样。',
     '42% 54%', '52% 54%', '52% 54%', 'wild'),
    ('长颈鹿', 'giraffe_2026072305', 'Giraffe', '🦒', 'giraffe.jpg', 'giraffe.mp3',
     '长颈鹿是地球上最高的陆地动物，脖子虽然很长，但颈椎骨数量和人类一样都是7块。',
     '49% 5%', '49% 15%', '49% 15%', 'wild'),
    ('斑马', 'zebra_2026072306', 'Zebra', '🦓', 'zebra.jpg', 'zebra.mp3',
     '斑马的黑白条纹不仅是伪装，还能防蚊虫叮咬。每只斑马的条纹图案都是独一无二的。',
     '67% 58%', '47% 58%', '62% 58%', 'wild'),
    ('猴子', 'monkey_2026072309', 'Monkey', '🐵', 'monkey.jpg', 'monkey.mp3',
     '猴子是灵长类动物中种类最丰富的一类，它们有复杂的社会结构，会使用工具和互相梳理毛发。',
     '45% 32%', '45% 82%', '45% 32%', 'wild'),
    ('松鼠', 'squirrel_2026072415', 'Squirrel', '🐿️', 'squirrel.jpg', 'squirrel.mp3',
     '松鼠每年会埋藏上千颗坚果，虽然它们会忘记其中很多藏匿点，但这些被遗忘的坚果会发芽长成新树。',
     '55% 50%', '70% 50%', '65% 50%', 'wild'),
    ('鹰', 'eagle_2026072418', 'Eagle', '🦅', 'eagle.jpg', 'eagle.mp3',
     '鹰的视力比人类敏锐8倍，能从几公里外看到地面上的小兔子。它们俯冲时速度可超过240公里每小时。',
     '50% 50%', '50% 50%', '50% 50%', 'wild'),
    ('猫头鹰', 'owl_2026072411', 'Owl', '🦉', 'owl.jpg', 'owl.mp3',
     '猫头鹰的头可以转动270度，因为它们有14节颈椎骨（人类只有7节）。它们能在完全黑暗中捕猎。',
     '50% 40%', '50% 40%', '50% 0%', 'wild'),
    ('鹦鹉', 'parrot_2026072419', 'Parrot', '🦜', 'parrot.jpg', 'parrot.mp3',
     '鹦鹉不仅会模仿人说话，还能理解一些词汇的含义。金刚鹦鹉的寿命可达60年以上。',
     '50% 30%', '50% 30%', '50% 32%', 'wild'),

    # ── 第二批（2026-07-24）20 只 ──
    # ── 🌍 野生动物（续）──
    ('北极熊', 'polar_bear_2026072401', 'Polar Bear', '🐻‍❄️', 'polarbear.jpg', 'polarbear.mp3',
     '北极熊的皮肤其实是黑色的，毛发是透明的，看起来白色是因为反射了光线。它们是游泳高手，能连续游好几天。',
     '40% 50%', '25% 50%', '25% 50%', 'wild'),
    ('豹子', 'leopard_2026072402', 'Leopard', '🐆', 'leopard.jpg', 'leopard.mp3',
     '豹子是短跑冠军，最高时速可达120公里。它们会把猎物拖到树上保存，防止被其他动物偷走。',
     '35% 50%', '35% 50%', '35% 50%', 'wild'),
    ('袋鼠', 'kangaroo_2026072403', 'Kangaroo', '🦘', 'kangaroo.jpg', 'kangaroo.mp3',
     '袋鼠宝宝出生时只有花生米大小，会在妈妈的育儿袋里继续发育半年以上。袋鼠只会向前跳不会向后退。',
     '55% 50%', '50% 50%', '50% 50%', 'wild'),
    ('河马', 'hippo_2026072405', 'Hippo', '🦛', 'hippo.jpg', 'hippo.mp3',
     '河马的皮肤会分泌一种红色的"防晒霜"，既能防晒又能抗菌。虽然看起来笨重，它们跑起来比人还快。',
     '85% 50%', '70% 50%', '70% 50%', 'wild'),
    ('狐狸', 'fox_2026072406', 'Fox', '🦊', 'fox.jpg', 'fox.mp3',
     '狐狸是聪明机灵的猎手，它们能听到地下老鼠的动静。北极狐的皮毛会随季节变色：冬天白色，夏天棕色。',
     '65% 50%', '100% 50%', '65% 60%', 'wild'),
    ('考拉', 'koala_2026072408', 'Koala', '🐨', 'koala.jpg', 'koala.mp3',
     '考拉每天要睡18-22个小时，它们只吃桉树叶，而且能从树叶中获取大部分水分，几乎不喝水。',
     '50% 50%', '25% 50%', '35% 30%', 'wild'),
    ('狼', 'wolf_2026072409', 'Wolf', '🐺', 'wolf.jpg', 'wolf.mp3',
     '狼是高度社会化的动物，狼群有严格的等级制度。它们的嚎叫可以和数公里外的同伴沟通。',
     '50% 50%', '50% 95%', '50% 55%', 'wild'),
    ('骆驼', 'camel_2026072410', 'Camel', '🐫', 'camel.jpg', 'camel.mp3',
     '骆驼的驼峰里储存的不是水而是脂肪，它们一次能喝下100升水，可以连续几天不喝水穿越沙漠。',
     '50% 50%', '37% 50%', '60% 50%', 'wild'),
    ('犀牛', 'rhino_2026072417', 'Rhino', '🦏', 'rhino.jpg', 'rhino.mp3',
     '犀牛是陆地上仅次于大象的第二大动物。它们的角由角蛋白组成，和人的指甲是同一种物质。',
     '30% 50%', '42% 50%', '40% 50%', 'wild'),

    # ── 🌊 海洋动物 ──
    ('海豚', 'dolphin_2026072308', 'Dolphin', '🐬', 'dolphin.jpg', 'dolphin.mp3',
     '海豚是非常聪明的海洋哺乳动物，它们用超声波定位和交流，睡觉时大脑一半休息一半保持清醒。',
     '42% 20%', '42% 50%', '42% 30%', 'ocean'),
    ('鱼', 'fish_2026072318', 'Fish', '🐟', 'fish.jpg', 'fish.mp3',
     '鱼类是地球上最古老的脊椎动物，已经存在超过5亿年。有些鱼能改变性别，有些能发电。',
     '87% 44%', '87% 44%', '87% 44%', 'ocean'),
    ('鲨鱼', 'shark_2026072321', 'Shark', '🦈', 'shark.jpg', 'shark.mp3',
     '鲨鱼比恐龙出现的时间还早，已经在地球上生存超过4亿年。它们一生会换掉超过3万颗牙齿。',
     '85% 50%', '90% 50%', '95% 50%', 'ocean'),
    ('鲸鱼', 'whale_2026072407', 'Whale', '🐋', 'whale.jpg', 'whale.mp3',
     '蓝鲸是地球上最大的动物，心脏有一辆小汽车那么大。鲸鱼的歌声可以在海洋中传播数百公里。',
     '30% 50%', '30% 50%', '30% 50%', 'ocean'),
    ('企鹅', 'penguin_2026072307', 'Penguin', '🐧', 'penguin.jpg', 'penguin.mp3',
     '企鹅是鸟类中的游泳高手，帝企鹅可以潜入500米深的海水中，憋气超过20分钟。',
     '46% 15%', '46% 15%', '46% 15%', 'ocean'),
    ('螃蟹', 'crab_2026072413', 'Crab', '🦀', 'crab.jpg', 'crab.mp3',
     '螃蟹横着走路是因为它们的腿关节只能向侧面弯曲。它们会脱壳长大，脱壳后身体是软的容易受伤。',
     '45% 50%', '45% 50%', '45% 50%', 'ocean'),

    # ── 🦎 爬虫和昆虫 ──
    ('鳄鱼', 'crocodile_2026072404', 'Crocodile', '🐊', 'crocodile.jpg', 'crocodile.mp3',
     '鳄鱼是恐龙时代的幸存者，已经在地球上生存超过2亿年。它们的大颚咬合力是所有动物中最强的。',
     '95% 50%', '95% 50%', '65% 50%', 'reptile'),
    ('蛇', 'snake_2026072414', 'Snake', '🐍', 'snake.jpg', 'snake.mp3',
     '蛇没有眼睑，所以它们永远睁着眼睛睡觉。它们用分叉的舌头来"闻"空气中的气味。',
     '50% 50%', '50% 50%', '50% 50%', 'reptile'),
    ('青蛙', 'frog_2026072320', 'Frog', '🐸', 'frog.jpg', 'frog.mp3',
     '青蛙的皮肤可以吸收水分和氧气，所以它们对环境污染特别敏感。它们是环境健康的"指示物种"。',
     '53% 56%', '33% 56%', '53% 56%', 'reptile'),
    ('乌龟', 'turtle_2026072416', 'Turtle', '🐢', 'turtle.jpg', 'turtle.mp3',
     '乌龟是地球上最长寿的动物之一，有些陆龟可以活到150岁以上。它们的壳其实是肋骨演化而来。',
     '60% 50%', '50% 50%', '50% 50%', 'reptile'),
    ('蝴蝶', 'butterfly_2026072319', 'Butterfly', '🦋', 'butterfly.jpg', 'butterfly.mp3',
     '蝴蝶用脚来尝味道！它们的翅膀上覆盖着细小的鳞片，这些鳞片能反射光线产生绚丽的色彩。',
     '54% 56%', '69% 56%', '54% 56%', 'reptile'),
    ('蜜蜂', 'bee_2026072412', 'Bee', '🐝', 'bee.jpg', 'bee.mp3',
     '一只蜜蜂一生只能产出约一茶匙的蜂蜜。它们通过跳"8字舞"来告诉同伴花朵的位置和距离。',
     '40% 50%', '55% 50%', '55% 50%', 'reptile'),

    # ====== 第3批（2026-07-29）12 只 ======
    # ── 🦎 爬虫和昆虫 ──
    ('蚂蚁', 'ant_2026072901', 'Ant', '🐜', 'ant.jpg', 'ant.mp3',
     '蚂蚁是地球上数量最多的昆虫之一，一个蚁群可以有几十万只蚂蚁。它们能搬起比自己重50倍的东西。',
     '50% 50%', '50% 50%', '50% 50%', 'reptile'),
    ('瓢虫', 'ladybug_2026072902', 'Ladybug', '🐞', 'ladybug.jpg', 'ladybug.mp3',
     '瓢虫背上有黑色斑点，7个点的最常见。它们是农民的好朋友，因为爱吃蚜虫这种害虫。',
     '50% 50%', '50% 50%', '50% 50%', 'reptile'),
    ('变色龙', 'chameleon_2026072903', 'Chameleon', '🦎', 'chameleon.jpg', 'chameleon.mp3',
     '变色龙变颜色不只是为了伪装，还为了表达情绪和调节体温。它们的眼睛可以独立转动！',
     '50% 50%', '50% 65%', '50% 50%', 'reptile'),
    ('蜥蜴', 'lizard_2026072904', 'Lizard', '🦎', 'lizard.jpg', 'lizard.mp3',
     '蜥蜴的尾巴断了还能重新长出来。它们在墙上爬行靠的是脚上细小的毛，能产生吸附力。',
     '70% 50%', '50% 50%', '50% 50%', 'reptile'),
    ('蜻蜓', 'dragonfly_2026072905', 'Dragonfly', '🦎', 'dragonfly.jpg', 'dragonfly.mp3',
     '蜻蜓是飞行高手，能向前飞、向后飞、悬停在空中。它们的眼睛由3万多只小眼睛组成！',
     '60% 50%', '60% 50%', '60% 50%', 'reptile'),
    ('蜗牛', 'snail_2026072906', 'Snail', '🐌', 'snail.jpg', 'snail.mp3',
     '蜗牛是地球上最慢的动物之一，但它们有两万六千多颗牙齿！蜗牛壳是随着身体一起长大的。',
     '50% 50%', '50% 50%', '50% 50%', 'reptile'),
    # ── 🌍 野生动物 ──
    ('刺猬', 'hedgehog_2026072907', 'Hedgehog', '🦔', 'hedgehog.jpg', 'hedgehog.mp3',
     '刺猬身上有大约5000根刺，遇到危险时会把身体卷成球。它们吃虫子，是花园里的小卫士。',
     '60% 50%', '50% 50%', '50% 50%', 'wild'),
    # ── 🏠 家里和农场 ──
    ('仓鼠', 'hamster_2026072908', 'Hamster', '🐹', 'hamster.jpg', 'hamster.mp3',
     '仓鼠的脸颊有像口袋一样的颊囊，可以塞满食物带回窝里。它们是很多小朋友养的第一种宠物。',
     '60% 50%', '50% 50%', '50% 50%', 'farm'),
    # ── 🌊 海洋动物 ──
    ('海龟', 'seaturtle_2026072909', 'Sea Turtle', '🐢', 'seaturtle.jpg', 'seaturtle.mp3',
     '海龟已经在地球上生活了超过1亿年，它们可以活到80岁以上。雌海龟会回到自己出生的海滩产卵。',
     '50% 65%', '60% 50%', '50% 65%', 'ocean'),
    ('章鱼', 'octopus_2026072910', 'Octopus', '🐙', 'octopus.jpg', 'octopus.mp3',
     '章鱼有三个心脏、九个大脑，血液是蓝色的。它们非常聪明，能打开瓶盖、模仿其他动物。',
     '50% 50%', '50% 50%', '50% 50%', 'ocean'),
    ('海马', 'seahorse_2026072911', 'Seahorse', '🌊', 'seahorse.jpg', 'seahorse.mp3',
     '海马爸爸负责孵宝宝！雌海马把卵产在雄海马的育儿袋里，爸爸怀孕生小海马。',
     '40% 50%', '40% 50%', '35% 50%', 'ocean'),
    ('海狮', 'sealion_2026072912', 'Sea Lion', '🦭', 'sealion.jpg', 'sealion.mp3',
     '海狮是海洋馆的明星，它们用鳍状肢在陆地上行走，在水里能憋气超过10分钟。',
     '30% 50%', '30% 50%', '35% 50%', 'ocean'),

    # ====== 第4批（2026-07-29）梅花鹿 ======
    ('鹿', 'deer_2026072913', 'Deer', '🦌', 'deer.jpg', 'deer.mp3',
     '鹿在夏天身上有白色斑点像梅花，到了冬天斑点就消失了。只有雄鹿长角，每年都会脱落重新长。',
     '60% 50%', '60% 50%', '60% 50%', 'wild'),

    # ====== 第5批（2026-07-29）中优先级 7 种 ======
    ('棕熊', 'brownbear_2026072914', 'Brown Bear', '🐻', 'brownbear.jpg', 'brownbear.mp3',
     '棕熊是体型最大的熊之一，冬天会冬眠。它们跑步速度能达到每小时50公里，比人快得多。',
     '37% 50%', '50% 50%', '50% 50%', 'wild'),
    ('大猩猩', 'gorilla_2026072915', 'Gorilla', '🦍', 'gorilla.jpg', 'gorilla.mp3',
     '大猩猩是最大的灵长类动物，和人类有98%的基因相同。它们会用手语和人类交流。',
     '50% 50%', '50% 50%', '50% 50%', 'wild'),
    ('孔雀', 'peacock_2026072916', 'Peacock', '🦚', 'peacock.jpg', 'peacock.mp3',
     '孔雀开屏时尾巴像一把巨大的扇子，上面有像眼睛一样的花纹。开屏是为了吸引雌孔雀。',
     '50% 60%', '50% 60%', '50% 60%', 'wild'),
    ('火烈鸟', 'flamingo_2026072917', 'Flamingo', '🦩', 'flamingo.jpg', 'flamingo.mp3',
     '火烈鸟为什么是粉色的？因为它们吃的虾和藻类里有红色素。它们单脚站立睡觉也不会倒。',
     '50% 20%', '50% 20%', '50% 20%', 'wild'),
    ('天鹅', 'swan_2026072918', 'Swan', '🦢', 'swan.jpg', 'swan.mp3',
     '天鹅是优雅的鸟类，终身只有一个伴侣。它们飞行时能飞到9000米高，是飞得最高的鸟类之一。',
     '25% 50%', '50% 50%', '50% 50%', 'wild'),
    ('萤火虫', 'firefly_2026072919', 'Firefly', '🪲', 'firefly.jpg', 'firefly.mp3',
     '萤火虫的尾部会发光，这是它们在寻找伴侣的信号。一只萤火虫的光由几十种化学反应控制。',
     '20% 50%', '30% 50%', '30% 50%', 'reptile'),
    ('蜘蛛', 'spider_2026072920', 'Spider', '🕷️', 'spider.jpg', 'spider.mp3',
     '蜘蛛不是昆虫，属于蛛形纲。它们吐的丝比钢铁还要坚韧，有些蜘蛛能织出直径2米的大网。',
     '50% 50%', '50% 50%', '50% 50%', 'reptile'),

    # ====== 第6批（2026-07-30）精选补充 6 种 ======
    ('水母', 'jellyfish_2026073001', 'Jellyfish', '🪼', 'jellyfish.jpg', 'jellyfish.mp3',
     '水母没有大脑、没有心脏、没有血液，但它们已经在地球上生活了超过6亿年。有些水母甚至可以永生。',
     '50% 50%', '50% 29%', '50% 5%', 'ocean'),
    ('海星', 'starfish_2026073002', 'Starfish', '⭐', 'starfish.jpg', 'starfish.mp3',
     '海星被切掉一条胳膊可以重新长出来，被切掉的胳膊也能长成一只全新的海星！',
     '50% 50%', '50% 50%', '50% 50%', 'ocean'),
    ('蝙蝠', 'bat_2026073003', 'Bat', '🦇', 'bat.jpg', 'bat.mp3',
     '蝙蝠是唯一会飞的哺乳动物。它们在黑暗中用超声波导航，能在完全看不见的情况下抓蚊子吃。',
     '50% 50%', '50% 50%', '50% 85%', 'wild'),
    ('树懒', 'sloth_2026073004', 'Sloth', '🦥', 'sloth.jpg', 'sloth.mp3',
     '树懒是世界上最慢的哺乳动物，每秒只能移动几厘米。它们大部分时间倒挂在树上，一周才下一次树。',
     '50% 50%', '50% 50%', '50% 50%', 'wild'),
    ('水獭', 'otter_2026073005', 'Otter', '🦦', 'otter.jpg', 'otter.mp3',
     '水獭是非常爱玩的小动物，经常仰面躺在水面上玩耍。它们有最喜欢的石头，用来敲开贝壳。',
     '40% 50%', '50% 50%', '50% 50%', 'wild'),
    ('老鼠', 'mouse_2026073006', 'Mouse', '🐭', 'mouse.jpg', 'mouse.mp3',
     '老鼠非常聪明，能学会走迷宫。它们的门牙一生都在生长，所以需要不停地咬东西来磨牙。',
     '40% 50%', '50% 50%', '50% 50%', 'farm'),
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
            for idx, item_tuple in enumerate(items):
                # 11-field tuple: name, code, en_name, emoji, img_file, audio_file,
                # fact, img_pos, img_pos_ipad_portrait, img_pos_ipad_landscape, group
                name, code, en_name, emoji, img_file, audio_file, fact, \
                    img_pos, img_pos_ipad_portrait, img_pos_ipad_landscape, group = item_tuple

                item = Item.objects.create(
                    category=cat,
                    code=code,
                    name=name,
                    english_name=en_name,
                    emoji=emoji,
                    fact=fact,
                    image_position=img_pos or "50% 50%",
                    image_position_ipad_portrait=img_pos_ipad_portrait or "50% 50%",
                    image_position_ipad_landscape=img_pos_ipad_landscape or "50% 50%",
                    image_position_checked=True,
                    sort_order=idx,
                    group=group or '',
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
