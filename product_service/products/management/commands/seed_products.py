from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import (
    Book,
    Camera,
    Category,
    Clothing,
    Headphones,
    HomeAppliance,
    Inventory,
    Laptop,
    Phone,
    Product,
    ProductImage,
    SmartWatch,
    Tablet,
    Toy,
)


CATEGORIES = [
    "Technology",
    "Education",
    "Entertainment",
    "Home",
    "Fashion & Lifestyle",
    "Family & Kids",
]

MODEL_BY_TYPE = {
    "book": Book,
    "laptop": Laptop,
    "phone": Phone,
    "toy": Toy,
    "tablet": Tablet,
    "headphones": Headphones,
    "camera": Camera,
    "smart_watch": SmartWatch,
    "home_appliance": HomeAppliance,
    "clothing": Clothing,
}

PRODUCTS = [
    {
        "type": "book",
        "category": "Technology",
        "name": "Python AI Engineering Handbook",
        "description": "Practical guide for building AI products, data pipelines, and model services.",
        "brand": "Ecom Books",
        "price": "289000",
        "details": {"author": "Linh Tran", "publisher": "CodePress", "isbn": "978604TECH001", "language": "Vietnamese", "page_count": 420},
    },
    {
        "type": "laptop",
        "category": "Technology",
        "name": "NovaBook Pro 14",
        "description": "Lightweight laptop for software development, study, and creative work.",
        "brand": "NovaTech",
        "price": "24500000",
        "details": {"cpu": "Intel Core Ultra 7", "ram_gb": 32, "storage_gb": 1024, "gpu": "Intel Arc", "screen_size_inch": "14.0"},
    },
    {
        "type": "phone",
        "category": "Technology",
        "name": "PixelWave S12",
        "description": "Android phone with a bright display, long battery life, and strong camera processing.",
        "brand": "PixelWave",
        "price": "13990000",
        "details": {"os": "Android", "storage_gb": 256, "ram_gb": 8, "camera_mp": 50, "battery_mah": 5000},
    },
    {
        "type": "toy",
        "category": "Technology",
        "name": "Junior Robotics Lab",
        "description": "Programmable robot kit for kids learning sensors, motors, and simple automation.",
        "brand": "BrightKids",
        "price": "1190000",
        "details": {"age_range": "8+", "material": "ABS plastic", "safety_standard": "CE"},
    },
    {
        "type": "tablet",
        "category": "Education",
        "name": "StudyTab 11",
        "description": "Tablet for online classes, note taking, ebooks, and lightweight productivity.",
        "brand": "EduMate",
        "price": "8990000",
        "details": {"os": "Android", "screen_size_inch": "11.0", "storage_gb": 128, "supports_pen": True},
    },
    {
        "type": "book",
        "category": "Education",
        "name": "Math Adventures Grade 5",
        "description": "Colorful math workbook with puzzles, examples, and practice exercises.",
        "brand": "Ecom Books",
        "price": "159000",
        "details": {"author": "Mai Nguyen", "publisher": "LearnHouse", "isbn": "978604EDU005", "language": "Vietnamese", "page_count": 180},
    },
    {
        "type": "toy",
        "category": "Education",
        "name": "STEM Magnetic Blocks",
        "description": "Magnetic construction set for spatial reasoning and creative engineering play.",
        "brand": "BrightKids",
        "price": "690000",
        "details": {"age_range": "4+", "material": "Magnet and ABS plastic", "safety_standard": "ASTM F963"},
    },
    {
        "type": "headphones",
        "category": "Entertainment",
        "name": "SoundWave Focus ANC",
        "description": "Noise cancelling headphones for music, travel, study, and remote meetings.",
        "brand": "SoundWave",
        "price": "3490000",
        "details": {"connection_type": "Bluetooth", "noise_cancelling": True, "battery_hours": 40},
    },
    {
        "type": "camera",
        "category": "Entertainment",
        "name": "Camora Vlog 4K",
        "description": "Compact mirrorless camera for travel videos, live streams, and family memories.",
        "brand": "Camora",
        "price": "18990000",
        "details": {"sensor_type": "APS-C CMOS", "megapixels": "24.2", "lens_mount": "C-Mount", "video_resolution": "4K"},
    },
    {
        "type": "toy",
        "category": "Entertainment",
        "name": "Family Strategy Quest",
        "description": "Easy-to-learn board game with cooperative missions and replayable scenarios.",
        "brand": "TableFun",
        "price": "520000",
        "details": {"age_range": "10+", "material": "Paper and cardboard", "safety_standard": "EN71"},
    },
    {
        "type": "home_appliance",
        "category": "Home",
        "name": "HomeChef Air Fryer 6L",
        "description": "Large air fryer for crisp family meals with less oil and fast cleanup.",
        "brand": "HomeChef",
        "price": "2190000",
        "details": {"appliance_type": "Air fryer", "power_watts": 1700, "capacity": "6L", "energy_rating": "A"},
    },
    {
        "type": "book",
        "category": "Home",
        "name": "Minimal Home Cooking",
        "description": "Simple recipes and weekly meal planning for busy households.",
        "brand": "Ecom Books",
        "price": "249000",
        "details": {"author": "An Pham", "publisher": "KitchenShelf", "isbn": "978604HOME011", "language": "Vietnamese", "page_count": 240},
    },
    {
        "type": "home_appliance",
        "category": "Technology",
        "name": "CleanMate Robot Vacuum X2",
        "description": "Smart robot vacuum with app scheduling, mapping, and automatic charging.",
        "brand": "CleanMate",
        "price": "7490000",
        "details": {"appliance_type": "Robot vacuum", "power_watts": 65, "capacity": "450ml dustbin", "energy_rating": "A+"},
    },
    {
        "type": "smart_watch",
        "category": "Fashion & Lifestyle",
        "name": "PulsePro Active Watch",
        "description": "Smart watch for workouts, sleep tracking, notifications, and daily health insights.",
        "brand": "PulsePro",
        "price": "4290000",
        "details": {"os": "Wear OS", "battery_days": 3, "water_resistant": True, "health_features": "Heart rate, SpO2, sleep"},
    },
    {
        "type": "clothing",
        "category": "Fashion & Lifestyle",
        "name": "UrbanTrail Water Resistant Jacket",
        "description": "Lightweight jacket for commute, travel, and changing weather.",
        "brand": "UrbanTrail",
        "price": "990000",
        "details": {"size": "L", "color": "Navy", "material": "Recycled polyester", "gender": "Unisex"},
    },
    {
        "type": "headphones",
        "category": "Fashion & Lifestyle",
        "name": "StreetBeat Mini Buds",
        "description": "Compact wireless earbuds for calls, workouts, and daily commuting.",
        "brand": "StreetBeat",
        "price": "1290000",
        "details": {"connection_type": "Bluetooth", "noise_cancelling": False, "battery_hours": 24},
    },
    {
        "type": "phone",
        "category": "Fashion & Lifestyle",
        "name": "Luma Flip",
        "description": "Stylish foldable phone with compact design and creator-friendly camera modes.",
        "brand": "Luma",
        "price": "22990000",
        "details": {"os": "Android", "storage_gb": 512, "ram_gb": 12, "camera_mp": 48, "battery_mah": 4300},
    },
    {
        "type": "tablet",
        "category": "Entertainment",
        "name": "CinemaPad OLED",
        "description": "OLED tablet for movies, cloud gaming, comics, and couch browsing.",
        "brand": "ViewPlus",
        "price": "12990000",
        "details": {"os": "Android", "screen_size_inch": "12.4", "storage_gb": 256, "supports_pen": False},
    },
    {
        "type": "camera",
        "category": "Technology",
        "name": "SecureCam Home 360",
        "description": "Indoor security camera with wide coverage, night vision, and app alerts.",
        "brand": "SecureCam",
        "price": "1490000",
        "details": {"sensor_type": "1/2.8 CMOS", "megapixels": "5.0", "lens_mount": "Fixed", "video_resolution": "2K"},
    },
    {
        "type": "laptop",
        "category": "Education",
        "name": "ClassBook Air 13",
        "description": "Affordable laptop for students, assignments, video classes, and browsing.",
        "brand": "EduMate",
        "price": "11990000",
        "details": {"cpu": "AMD Ryzen 5", "ram_gb": 16, "storage_gb": 512, "gpu": "Integrated Radeon", "screen_size_inch": "13.3"},
    },
    {
        "type": "clothing",
        "category": "Family & Kids",
        "name": "BrightKids Cotton Hoodie",
        "description": "Soft cotton hoodie for kids with durable stitching and playful colors.",
        "brand": "BrightKids",
        "price": "390000",
        "details": {"size": "Kids M", "color": "Green", "material": "Cotton blend", "gender": "Kids"},
    },
    {
        "type": "toy",
        "category": "Family & Kids",
        "name": "Remote Control Dino Rover",
        "description": "Rechargeable remote-control dinosaur rover with lights and sound effects.",
        "brand": "RacerBox",
        "price": "790000",
        "details": {"age_range": "6+", "material": "ABS plastic", "safety_standard": "CE"},
    },
    {
        "type": "smart_watch",
        "category": "Technology",
        "name": "KidSafe GPS Watch",
        "description": "Smart watch for kids with GPS location, family contacts, and activity tracking.",
        "brand": "KidSafe",
        "price": "1990000",
        "details": {"os": "KidSafe OS", "battery_days": 2, "water_resistant": True, "health_features": "Steps, SOS, location"},
    },
    {
        "type": "home_appliance",
        "category": "Family & Kids",
        "name": "PureNest Air Purifier Mini",
        "description": "Quiet air purifier for bedrooms, study corners, and baby rooms.",
        "brand": "PureNest",
        "price": "2690000",
        "details": {"appliance_type": "Air purifier", "power_watts": 35, "capacity": "25m2 room", "energy_rating": "A"},
    },
]


class Command(BaseCommand):
    help = "Seed typed demo ecommerce products."

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()

        categories = {
            name: Category.objects.create(name=name, slug=slugify(name))
            for name in CATEGORIES
        }

        for index, item in enumerate(PRODUCTS, start=1):
            model_class = MODEL_BY_TYPE[item["type"]]
            product = model_class.objects.create(
                name=item["name"],
                slug=slugify(item["name"]),
                description=item["description"],
                price=Decimal(item["price"]),
                category=categories[item["category"]],
                brand=item["brand"],
                status="ACTIVE",
                **item["details"],
            )
            Inventory.objects.create(product=product, quantity=20 + (index * 3), reserved_quantity=0)
            ProductImage.objects.create(
                product=product,
                is_primary=True,
                image_url=f"https://picsum.photos/seed/typed-product-{index}/640/640",
                alt_text=item["name"],
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} typed demo ecommerce products."))
