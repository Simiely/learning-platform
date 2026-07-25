# Rename image_position_ipad -> image_position_ipad_portrait + add landscape

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_item_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='image_position_ipad',
            new_name='image_position_ipad_portrait',
        ),
        migrations.AddField(
            model_name='item',
            name='image_position_ipad_landscape',
            field=models.CharField(
                blank=True, default='50% 50%', max_length=30,
                verbose_name='iPad 横屏焦点',
                help_text='iPad 横屏图片焦点, CSS object-position 格式'
            ),
        ),
    ]
