from django.contrib import admin
from .models import Category, Item, LearningProgress, QuizAttempt


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    fields = ('name', 'english_name', 'emoji', 'fact', 'image', 'audio', 'audio_en', 'audio_fact', 'sort_order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'item_count', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ItemInline]
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sort_order')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('category', 'sort_order')


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'learned', 'view_count', 'last_viewed')
    list_filter = ('learned', 'item__category')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'correct', 'total', 'accuracy', 'quiz_type', 'created_at')
    list_filter = ('category', 'quiz_type')
    readonly_fields = ('accuracy',)
