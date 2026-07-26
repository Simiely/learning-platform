import sys
from django.core.management.base import BaseCommand
from apps.core.models import Item


class Command(BaseCommand):
    help = (
        "Sync image_position fields (iPhone + iPad portrait + iPad landscape) "
        "from seed_data ANIMALS table into existing DB items. "
        "Does NOT touch other fields; safe to run on live data."
    )

    def handle(self, *args, **options):
        from apps.core.management.commands.seed_data import ANIMALS

        updated = 0
        missing = []
        update_fields_map = {
            'image_position': 'img_pos',
            'image_position_ipad_portrait': 'img_pos_ipad_portrait',
            'image_position_ipad_landscape': 'img_pos_ipad_landscape',
        }

        for name, code, english_name, emoji, img_file, audio_file, fact, img_pos, img_pos_ipad_portrait, img_pos_ipad_landscape in ANIMALS:
            try:
                item = Item.objects.get(code=code)
            except Item.DoesNotExist:
                missing.append(f"{name}({code})")
                continue

            changed_fields = []
            for field_name, seed_val_key in update_fields_map.items():
                seed_val = locals()[seed_val_key]
                if seed_val and getattr(item, field_name) != seed_val:
                    old = getattr(item, field_name)
                    setattr(item, field_name, seed_val)
                    changed_fields.append((field_name, old, seed_val))

            if changed_fields:
                update_fields = [f for f, _, _ in changed_fields]
                item.image_position_checked = True
                update_fields.append('image_position_checked')
                item.save(update_fields=update_fields)
                for field, old, new in changed_fields:
                    self.stdout.write(
                        self.style.SUCCESS(f"  {name} {field}: {old} -> {new}")
                    )
                updated += 1

        if updated:
            self.stdout.write(
                self.style.SUCCESS(f"\nUpdated {updated} item(s) (iPhone + iPad portrait + iPad landscape).")
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
