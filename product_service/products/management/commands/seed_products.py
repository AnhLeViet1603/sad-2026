from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Inventory, Product, ProductAttribute, ProductAttributeValue, ProductImage


CATEGORIES = [
    "Electronics",
    "Home & Kitchen",
    "Fashion",
    "Beauty & Health",
    "Sports & Outdoor",
    "Toys & Games",
]

PRODUCTS = [
    ("Electronics", "Noise Canceling Headphones", "A wireless headset for focused work, travel, and daily calls.", "SoundWave"),
    ("Electronics", "Smart Fitness Watch", "Tracks workouts, sleep, heart rate, and daily productivity reminders.", "PulsePro"),
    ("Electronics", "Portable Bluetooth Speaker", "Compact speaker with clear sound for home, office, and outdoor use.", "SoundWave"),
    ("Electronics", "USB-C Fast Charging Hub", "Multi-port charging hub for phones, tablets, laptops, and accessories.", "Voltix"),
    ("Electronics", "4K Action Camera", "Durable action camera for travel, sports, and content creation.", "Camora"),
    ("Home & Kitchen", "Air Fryer Oven", "Countertop air fryer for quick meals with less oil.", "HomeChef"),
    ("Home & Kitchen", "Robot Vacuum Cleaner", "Smart vacuum for scheduled cleaning across multiple rooms.", "CleanMate"),
    ("Home & Kitchen", "Ceramic Cookware Set", "Non-stick cookware set for everyday cooking.", "KitchenPro"),
    ("Home & Kitchen", "Ergonomic Office Chair", "Adjustable chair for long work sessions and home offices.", "WorkWell"),
    ("Home & Kitchen", "LED Desk Lamp", "Dimmable desk lamp with warm and cool light modes.", "Brightly"),
    ("Fashion", "Everyday Canvas Backpack", "Lightweight backpack with laptop storage and travel pockets.", "UrbanTrail"),
    ("Fashion", "Classic White Sneakers", "Comfortable sneakers for casual outfits and daily walks.", "StreetForm"),
    ("Fashion", "Water Resistant Jacket", "Light jacket for commute, travel, and changing weather.", "UrbanTrail"),
    ("Fashion", "Leather Card Wallet", "Slim wallet with quick-access slots for cards and cash.", "NomadGoods"),
    ("Fashion", "Cotton Graphic T-Shirt", "Soft cotton tee designed for everyday wear.", "StreetForm"),
    ("Beauty & Health", "Hydrating Skincare Set", "Daily skincare set with cleanser, serum, and moisturizer.", "GlowLab"),
    ("Beauty & Health", "Electric Toothbrush", "Rechargeable toothbrush with multiple cleaning modes.", "SmileCare"),
    ("Beauty & Health", "Aromatherapy Diffuser", "Quiet diffuser for essential oils and room ambience.", "CalmSpace"),
    ("Beauty & Health", "Digital Body Scale", "Smart scale for tracking weight and body metrics.", "PulsePro"),
    ("Beauty & Health", "Massage Therapy Gun", "Portable massage device for recovery and muscle relaxation.", "FlexFit"),
    ("Sports & Outdoor", "Adjustable Dumbbell Pair", "Space-saving dumbbells for home strength training.", "FlexFit"),
    ("Sports & Outdoor", "Yoga Mat Pro", "Non-slip mat for yoga, stretching, and floor workouts.", "ZenMove"),
    ("Sports & Outdoor", "Insulated Water Bottle", "Keeps drinks cold or warm during workouts and travel.", "TrailCup"),
    ("Sports & Outdoor", "Camping Lantern", "Rechargeable lantern for camping, emergencies, and outdoor nights.", "CampLite"),
    ("Sports & Outdoor", "Running Waist Pack", "Compact waist pack for phone, keys, and running essentials.", "Runly"),
    ("Toys & Games", "STEM Building Blocks", "Creative construction set for hands-on learning and play.", "BrightKids"),
    ("Toys & Games", "Family Strategy Board Game", "Easy-to-learn strategy game for family game nights.", "TableFun"),
    ("Toys & Games", "Remote Control Car", "Rechargeable RC car for indoor and outdoor racing.", "RacerBox"),
    ("Toys & Games", "Kids Art Supply Kit", "Drawing and craft kit with markers, paper, and accessories.", "BrightKids"),
    ("Toys & Games", "Puzzle Adventure Set", "Colorful puzzle set for focus, memory, and problem solving.", "TableFun"),
]


class Command(BaseCommand):
    help = "Seed demo ecommerce products."

    def handle(self, *args, **options):
        Product.objects.filter(brand__in=["Ecom Books", "MicroShop Demo"]).delete()

        categories = {
            name: Category.objects.get_or_create(name=name, slug=slugify(name))[0]
            for name in CATEGORIES
        }
        brand_attr, _ = ProductAttribute.objects.get_or_create(code="brand", defaults={"name": "Brand"})
        warranty_attr, _ = ProductAttribute.objects.get_or_create(code="warranty", defaults={"name": "Warranty"})

        for index, (category_name, name, description, brand) in enumerate(PRODUCTS, start=1):
            category = categories[category_name]
            product, _ = Product.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": description,
                    "price": Decimal("149000") + Decimal(index * 85000),
                    "category": category,
                    "brand": "MicroShop Demo",
                    "status": "ACTIVE",
                },
            )
            Inventory.objects.update_or_create(
                product=product,
                defaults={"quantity": 18 + index, "reserved_quantity": 0},
            )
            ProductImage.objects.update_or_create(
                product=product,
                is_primary=True,
                defaults={
                    "image_url": f"https://picsum.photos/seed/ecom-{index}/640/640",
                    "alt_text": name,
                },
            )
            ProductAttributeValue.objects.update_or_create(
                product=product,
                attribute=brand_attr,
                defaults={"value": brand},
            )
            ProductAttributeValue.objects.update_or_create(
                product=product,
                attribute=warranty_attr,
                defaults={"value": "12 months"},
            )

        self.stdout.write(self.style.SUCCESS("Seeded 30 demo ecommerce products."))
