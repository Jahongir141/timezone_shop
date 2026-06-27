"""
Management command to populate the database with sample data.
Usage: python manage.py seed_data
"""
import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from store.models import Category, Watch

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


CATEGORY_NAMES = ["Luxury", "Sport", "Smart", "Classic", "Casual", "Digital"]

BRANDS = ["Rolex", "Casio", "Seiko", "Tissot", "Fossil", "Citizen", "Garmin", "Omega"]

MOVEMENTS = ["Automatic", "Quartz", "Mechanical", "Solar", "Kinetic"]
CASE_MATERIALS = ["Stainless Steel", "Titanium", "Ceramic", "Gold-Plated", "Carbon Fiber"]
STRAP_MATERIALS = ["Leather", "Rubber", "Stainless Steel", "Nylon", "Silicone"]
WATER_RESISTANCE = ["30m", "50m", "100m", "200m", "300m"]
GENDERS = ["men", "women", "unisex"]

COLORS = [
    (47, 111, 237), (28, 28, 35), (210, 180, 70),
    (90, 90, 100), (180, 40, 60), (40, 150, 110),
]


def generate_watch_image(text, color):
    """Generate a simple placeholder watch image using Pillow."""
    img = Image.new("RGB", (600, 600), color=color)
    draw = ImageDraw.Draw(img)
    # Draw a circle to look like a watch face
    draw.ellipse((150, 100, 450, 400), outline=(255, 255, 255), width=10)
    draw.ellipse((270, 220, 330, 280), fill=(255, 255, 255))
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((220, 430), text, fill=(255, 255, 255), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"{text.replace(' ', '_').lower()}.jpg")


class Command(BaseCommand):
    help = "Seed the database with sample categories, watches and a superuser."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing Watch and Category data before seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            Watch.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing watch data."))

        categories = {}
        for name in CATEGORY_NAMES:
            category, created = Category.objects.get_or_create(name=name)
            categories[name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))

        if not PIL_AVAILABLE:
            self.stdout.write(self.style.ERROR("Pillow is not installed. Cannot generate images."))
            return

        watch_count = 0
        titles_used = set()

        for category_name, category in categories.items():
            for i in range(6):
                brand = random.choice(BRANDS)
                model_code = f"{brand[:2].upper()}-{random.randint(100, 999)}"
                title = f"{brand} {category_name} {model_code}"

                if title in titles_used:
                    continue
                titles_used.add(title)

                color = random.choice(COLORS)
                image_file = generate_watch_image(f"{brand}", color)

                watch = Watch(
                    category=category,
                    brand=brand,
                    model=model_code,
                    title=title,
                    description=(
                        f"The {title} combines {random.choice(MOVEMENTS).lower()} movement "
                        f"with a premium {random.choice(CASE_MATERIALS).lower()} case, "
                        f"designed for everyday elegance and durability. "
                        f"Perfect for those who value precision and style."
                    ),
                    price=round(random.uniform(49.99, 2999.99), 2),
                    stock=random.randint(0, 40),
                    movement=random.choice(MOVEMENTS),
                    case_material=random.choice(CASE_MATERIALS),
                    strap_material=random.choice(STRAP_MATERIALS),
                    water_resistance=random.choice(WATER_RESISTANCE),
                    gender=random.choice(GENDERS),
                    is_featured=(i == 0),
                    is_new_arrival=(i == 1),
                )
                watch.image.save(image_file.name, image_file, save=False)
                watch.save()
                watch_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {watch_count} sample watches."))

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@timezone.com", password="admin12345"
            )
            self.stdout.write(self.style.SUCCESS(
                "Created superuser -> username: admin | password: admin12345"
            ))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))
