from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Inventory, Product, ProductAttribute, ProductAttributeValue, ProductImage


CATEGORIES = [
    "Sách lập trình",
    "Sách AI/Data",
    "Sách kinh tế",
    "Sách ngoại ngữ",
    "Sách kỹ năng",
    "Sách thiếu nhi",
]

PRODUCT_NAMES = [
    "Python thực chiến",
    "Django REST Framework căn bản",
    "Clean Code cho lập trình viên",
    "Kiến trúc Microservices",
    "Docker và Kubernetes nhập môn",
    "Machine Learning cơ bản",
    "Deep Learning ứng dụng",
    "Data Engineering với Python",
    "SQL cho phân tích dữ liệu",
    "Trí tuệ nhân tạo trong kinh doanh",
    "Tư duy tài chính cá nhân",
    "Marketing hiện đại",
    "Khởi nghiệp tinh gọn",
    "Quản trị sản phẩm số",
    "Kế toán cho nhà quản lý",
    "English Grammar in Use",
    "IELTS Vocabulary Builder",
    "Giao tiếp tiếng Anh công sở",
    "Tiếng Nhật nhập môn",
    "TOEIC chiến lược 750+",
    "Kỹ năng giao tiếp",
    "Tư duy phản biện",
    "Quản lý thời gian",
    "Làm việc sâu",
    "Thói quen hiệu quả",
    "Toán vui cho trẻ",
    "Khoa học quanh em",
    "Truyện kể trước giờ ngủ",
    "Khám phá thế giới động vật",
    "Lập trình Scratch cho thiếu nhi",
]


class Command(BaseCommand):
    help = "Seed demo bookstore products."

    def handle(self, *args, **options):
        categories = {
            name: Category.objects.get_or_create(name=name, slug=slugify(name))[0]
            for name in CATEGORIES
        }
        publisher_attr, _ = ProductAttribute.objects.get_or_create(code="publisher", defaults={"name": "Nhà xuất bản"})
        level_attr, _ = ProductAttribute.objects.get_or_create(code="level", defaults={"name": "Mức độ"})

        for index, name in enumerate(PRODUCT_NAMES, start=1):
            category = categories[CATEGORIES[(index - 1) // 5]]
            product, created = Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": f"{name} là sách demo phục vụ luồng e-commerce và AI recommendation.",
                    "price": Decimal("99000") + Decimal(index * 7000),
                    "category": category,
                    "brand": "Ecom Books",
                    "status": "ACTIVE",
                },
            )
            if created:
                Inventory.objects.create(product=product, quantity=20 + index, reserved_quantity=0)
                ProductImage.objects.create(
                    product=product,
                    image_url=f"https://picsum.photos/seed/book-{index}/480/640",
                    alt_text=name,
                    is_primary=True,
                )
                ProductAttributeValue.objects.create(product=product, attribute=publisher_attr, value="Ecom Publishing")
                ProductAttributeValue.objects.create(product=product, attribute=level_attr, value="Cơ bản")

        self.stdout.write(self.style.SUCCESS("Seeded 30 demo products."))

