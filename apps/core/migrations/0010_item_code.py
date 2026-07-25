# Generated manually — adds code field + auto-generates codes for existing animals

from django.db import migrations, models


def generate_codes(apps, schema_editor):
    """Generate codes like polar_bear_2026072401 based on english_name + position."""
    Item = apps.get_model('core', 'Item')
    cats = apps.get_model('core', 'Category').objects.filter(slug='animals')
    if not cats.exists():
        return
    items = Item.objects.filter(category=cats[0]).order_by('sort_order', 'id')

    # Original 21: date 20260723, new 20: date 20260724
    for idx, item in enumerate(items):
        en_slug = item.english_name.lower().replace(' ', '_').replace('-', '_')
        if idx < 21:
            code = f"{en_slug}_20260723{idx + 1:02d}"
        else:
            code = f"{en_slug}_20260724{idx - 20:02d}"
        item.code = code
        item.save(update_fields=['code'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_alter_learningprogress_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='code',
            field=models.CharField(
                blank=True, default='', max_length=50,
                verbose_name='唯一标识'
            ),
        ),
        # Populate codes for existing items before making field unique
        migrations.RunPython(generate_codes, migrations.RunPython.noop),
        # Now safe to add unique constraint
        migrations.AlterField(
            model_name='item',
            name='code',
            field=models.CharField(
                blank=True, default='', max_length=50, unique=True,
                verbose_name='唯一标识',
                help_text='英文小写+日期序号，如 polar_bear_2026072401。改名不影响匹配。'
            ),
        ),
    ]
