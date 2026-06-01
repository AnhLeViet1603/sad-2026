from django.core.management.base import BaseCommand

from staff.models import Permission, Role


DEFAULT_PERMISSIONS = [
    ("product.manage", "Manage products"),
    ("order.manage", "Manage orders"),
    ("staff.manage", "Manage staff"),
    ("dashboard.view", "View dashboard"),
]

DEFAULT_ROLES = {
    "ADMIN": ["product.manage", "order.manage", "staff.manage", "dashboard.view"],
    "STAFF": ["dashboard.view"],
    "PRODUCT_MANAGER": ["product.manage", "dashboard.view"],
    "ORDER_MANAGER": ["order.manage", "dashboard.view"],
}


class Command(BaseCommand):
    help = "Seed default staff roles and permissions."

    def handle(self, *args, **options):
        permissions = {}
        for code, name in DEFAULT_PERMISSIONS:
            permission, _ = Permission.objects.get_or_create(code=code, defaults={"name": name})
            permissions[code] = permission

        for role_name, permission_codes in DEFAULT_ROLES.items():
            role, _ = Role.objects.get_or_create(name=role_name)
            role.permissions.set([permissions[code] for code in permission_codes])

        self.stdout.write(self.style.SUCCESS("Seeded staff roles and permissions."))

