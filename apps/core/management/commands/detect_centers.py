import os
from django.core.management.base import BaseCommand
from apps.core.models import Item, Category
from apps.core.image_utils import detect_image_center


class Command(BaseCommand):
    help = (
        "Auto-detect visual focus center (image_position) for unchecked images.\n"
        "NOTE: items with image_position_checked=True are skipped unless --force.\n"
        "The seed data has hand-tuned positions — do NOT --force on them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--category', type=str, default='',
            help='Limit to specific category slug (e.g. "animals")'
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Re-detect even already-checked images'
        )

    def handle(self, *args, **options):
        qs = Item.objects.all()
        if options['category']:
            qs = qs.filter(category__slug=options['category'])
        if not options['force']:
            qs = qs.filter(image_position_checked=False)

        # Only items with actual image files
        qs = qs.exclude(image='')

        total = qs.count()
        if total == 0:
            self.stdout.write('No items need detection.')
            return

        self.stdout.write(f'Found {total} items to process ...')
        ok = 0
        fail = 0

        for item in qs:
            try:
                path = item.image.path
            except NotImplementedError:
                # Non-local storage backend (e.g. S3) — skip
                item.image_position_checked = True
                item.save(update_fields=["image_position_checked"])
                fail += 1
                continue
            if not os.path.exists(path):
                item.image_position_checked = True
                item.save(update_fields=["image_position_checked"])
                fail += 1
                continue
            pos = detect_image_center(path)
            if pos:
                item.image_position = pos
                item.image_position_checked = True
                item.save(update_fields=['image_position', 'image_position_checked'])
                ok += 1
            else:
                # Mark as checked anyway so we don't retry
                item.image_position_checked = True
                item.save(update_fields=['image_position_checked'])
                fail += 1
                self.stdout.write(f'  FAIL: {item.name} (no edges detected)')

        self.stdout.write(self.style.SUCCESS(
            f'Done: {ok} detected, {fail} failed (marked checked)'
        ))
