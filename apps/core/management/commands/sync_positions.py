import sys
from django.core.management.base import BaseCommand
from apps.core.models import Item


class Command(BaseCommand):
    help = (
        "Sync image_position from seed_data ANIMALS table into existing DB items. "
        "Does NOT touch other fields; safe to run on live data."
    )

    def handle(self, *args, **options):
        from apps.core.management.commands.seed_data import ANIMALS

        updated = 0
        missing = []

        for name, english_name, emoji, img_file, audio_file, fact, img_pos in ANIMALS:
            try:
                item = Item.objects.get(name=name)
            except Item.DoesNotExist:
                missing.append(name)
                continue

            if img_pos and item.image_position != img_pos:
                old = item.image_position
                item.image_position = img_pos
                item.image_position_checked = True
                item.save(update_fields=["image_position", "image_position_checked"])
                self.stdout.write(
                    self.style.SUCCESS(f"  {name}: {old} -> {img_pos}")
                )
                updated += 1

        if updated:
            self.stdout.write(
                self.style.SUCCESS(f"\nUpdated {updated} item position(s).")
            )
        else:
            self.stdout.write("All positions already up to date.")

        if missing:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {len(missing)} items not in DB: {', '.join(missing)}"
                )
            )
        sys.exit(0)
