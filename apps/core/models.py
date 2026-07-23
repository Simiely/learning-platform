from __future__ import annotations

from typing import Any

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='标识')
    icon = models.CharField(
        max_length=20, default='folder',
        verbose_name='图标',
        help_text='一个 emoji 或图标字符'
    )
    description = models.TextField(blank=True, default='', verbose_name='描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '学习模块'
        verbose_name_plural = '学习模块'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name

    def item_count(self):
        return self.items.count()
    item_count.short_description = '条目数'


class Item(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='items', verbose_name='所属模块'
    )
    name = models.CharField(max_length=200, verbose_name='名称')
    english_name = models.CharField(max_length=200, blank=True, default='', verbose_name='英文名称')
    emoji = models.CharField(max_length=50, blank=True, default='', verbose_name='表情符号')
    fact = models.TextField(blank=True, default='', verbose_name='科普知识',
                            help_text='点击可播放语音的科普说明文字')
    image = models.ImageField(
        upload_to='images/', blank=True, null=True,
        verbose_name='图片'
    )
    image_position = models.CharField(
        max_length=30, blank=True, default='50% 50%',
        verbose_name='图片焦点', help_text='自动检测的视觉中心, CSS object-position 格式'
    )
    image_position_checked = models.BooleanField(
        default=False, verbose_name='焦点已检测',
        help_text='是否已经自动检测过图片视觉中心'
    )
    audio = models.FileField(
        upload_to='audio/', blank=True, null=True,
        verbose_name='中文语音'
    )
    audio_en = models.FileField(
        upload_to='audio_en/', blank=True, null=True,
        verbose_name='英文语音'
    )
    audio_fact = models.FileField(
        upload_to='audio_fact/', blank=True, null=True,
        verbose_name='科普语音'
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '学习条目'
        verbose_name_plural = '学习条目'
        ordering = ['category', 'sort_order', 'id']

    def __str__(self):
        return f'{self.name} ({self.category.name})'

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict used by cards view and item_detail_api."""
        return {
            "id": self.id,
            "name": self.name,
            "english_name": self.english_name,
            "emoji": self.emoji,
            "fact": self.fact,
            "image": self.image.url if self.image else "",
            "image_position": self.image_position or "50% 50%",
            "audio_zh": self.audio.url if self.audio else "",
            "audio_en": self.audio_en.url if self.audio_en else "",
            "audio_fact": self.audio_fact.url if self.audio_fact else "",
        }


class LearningProgress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='learning_progress', verbose_name='用户'
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        related_name='progress', verbose_name='学习条目'
    )
    learned = models.BooleanField(default=False, verbose_name='已学会')
    view_count = models.IntegerField(default=1, verbose_name='查看次数')
    last_viewed = models.DateTimeField(auto_now=True, verbose_name='最近查看')

    class Meta:
        verbose_name = '学习进度'
        verbose_name_plural = '学习进度'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'item'],
                name='unique_user_item_progress',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.item.name}'


class QuizAttempt(models.Model):
    QUIZ_TYPES = [
        ('image_to_name', '看图选名'),
        ('name_to_image', '看名选图'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='quiz_attempts', verbose_name='用户'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        verbose_name='学习模块'
    )
    total = models.IntegerField(default=0, verbose_name='总题数')
    correct = models.IntegerField(default=0, verbose_name='答对数')
    quiz_type = models.CharField(
        max_length=20, default='image_to_name',
        choices=QUIZ_TYPES,
        verbose_name='测验类型'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '测验记录'
        verbose_name_plural = '测验记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.category.name} ({self.correct}/{self.total})'

    @property
    def accuracy(self):
        if self.total == 0:
            return 0
        return round(self.correct / self.total * 100)
