"""Jobs category seed data.

图片暂用 emoji 代替（img_file 留空），后续补充真实图片时再填入文件名。
分组：医护 / 救援 / 交通 / 教育 / 餐饮 / 运动 / 科学 / 艺术
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    name: str
    code: str
    english_name: str
    emoji: str
    img_file: str
    audio_file: str
    fact: str
    image_position: str = "50% 50%"
    image_position_ipad_portrait: str = "50% 50%"
    image_position_ipad_landscape: str = "50% 50%"
    group: str = ""


JOB_GROUPS = {
    "medical": "👨‍⚕️ 医护",
    "rescue": "👨‍🚒 救援",
    "transport": "👨‍✈️ 交通",
    "education": "👩‍🏫 教育",
    "food": "👨‍🍳 餐饮",
    "sport": "🏃 运动",
    "science": "🔬 科学",
    "art": "🎨 艺术",
}


ITEMS: list[Job] = [
    # ---- 医护 ----
    Job("医生", "doctor_2026080101", "Doctor", "👨‍⚕️", "", "doctor.mp3",
        "医生帮我们看病、治病，还会告诉我们要怎么保持健康。", "50% 50%", "50% 50%", "50% 50%", "medical"),
    Job("护士", "nurse_2026080102", "Nurse", "👩‍⚕️", "", "nurse.mp3",
        "护士细心地照顾病人，打针、换药、量体温，是医生的好帮手。", "50% 50%", "50% 50%", "50% 50%", "medical"),
    # ---- 救援 ----
    Job("消防员", "firefighter_2026080103", "Firefighter", "👨‍🚒", "", "firefighter.mp3",
        "消防员负责灭火和救人，遇到火灾要勇敢地冲在最前面。", "50% 50%", "50% 50%", "50% 50%", "rescue"),
    Job("警察", "police_officer_2026080104", "Police Officer", "👮", "", "police_officer.mp3",
        "警察保护大家的安全，抓坏人、指挥交通，有困难可以找警察叔叔。", "50% 50%", "50% 50%", "50% 50%", "rescue"),
    # ---- 交通 ----
    Job("飞行员", "pilot_2026080105", "Pilot", "👨‍✈️", "", "pilot.mp3",
        "飞行员驾驶飞机，载着乘客飞过高山和大海，到达世界各地。", "50% 50%", "50% 50%", "50% 50%", "transport"),
    Job("宇航员", "astronaut_2026080106", "Astronaut", "👨‍🚀", "", "astronaut.mp3",
        "宇航员乘坐火箭飞向太空，在空间站里做实验，在太空里会飘起来。", "50% 50%", "50% 50%", "50% 50%", "transport"),
    # ---- 教育 ----
    Job("老师", "teacher_2026080107", "Teacher", "👩‍🏫", "", "teacher.mp3",
        "老师教我们读书写字，解答我们的问题，陪我们一起长大。", "50% 50%", "50% 50%", "50% 50%", "education"),
    Job("学生", "student_2026080108", "Student", "🧑‍🎓", "", "student.mp3",
        "学生每天在学校学习新知识，认真听讲、完成作业，慢慢长大。", "50% 50%", "50% 50%", "50% 50%", "education"),
    # ---- 餐饮 ----
    Job("厨师", "chef_2026080109", "Chef", "👨‍🍳", "", "chef.mp3",
        "厨师戴着高高的白帽子，做出美味的饭菜，让大家吃得开心。", "50% 50%", "50% 50%", "50% 50%", "food"),
    Job("农民", "farmer_2026080110", "Farmer", "🧑‍🌾", "", "farmer.mp3",
        "农民伯伯种粮食和蔬菜，我们每天吃的米饭和水果都是他们的劳动成果。", "50% 50%", "50% 50%", "50% 50%", "food"),
    # ---- 运动 ----
    Job("运动员", "athlete_2026080111", "Athlete", "🏃", "", "athlete.mp3",
        "运动员每天刻苦训练，在比赛场上拼搏，为国家和自己争取荣誉。", "50% 50%", "50% 50%", "50% 50%", "sport"),
    Job("游泳运动员", "swimmer_2026080112", "Swimmer", "🏊", "", "swimmer.mp3",
        "游泳运动员在水里游得飞快，比赛时要拼尽全力冲向终点。", "50% 50%", "50% 50%", "50% 50%", "sport"),
    # ---- 科学 ----
    Job("科学家", "scientist_2026080113", "Scientist", "🔬", "", "scientist.mp3",
        "科学家做实验、研究新知识，发明新东西，帮人类解决难题。", "50% 50%", "50% 50%", "50% 50%", "science"),
    Job("工程师", "engineer_2026080114", "Engineer", "👷", "", "engineer.mp3",
        "工程师设计和建造桥梁、大楼、机器，让我们的城市越来越美好。", "50% 50%", "50% 50%", "50% 50%", "science"),
    # ---- 艺术 ----
    Job("画家", "artist_2026080115", "Artist", "👨‍🎨", "", "artist.mp3",
        "画家用画笔和颜料画出美丽的画，用作品表达自己的想法和情感。", "50% 50%", "50% 50%", "50% 50%", "art"),
    Job("歌手", "singer_2026080116", "Singer", "🎤", "", "singer.mp3",
        "歌手用歌声给大家带来快乐，在舞台上闪闪发光，唱出动听的歌曲。", "50% 50%", "50% 50%", "50% 50%", "art"),
]
