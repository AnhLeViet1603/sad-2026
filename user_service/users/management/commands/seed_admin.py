from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db.models import Q

from users.models import User


class Command(BaseCommand):
    help = "Create or update the default application admin account."

    def handle(self, *args, **options):
        admin = User.objects.filter(Q(username="admin") | Q(email="admin@example.com")).first()
        created = admin is None
        if created:
            admin = User(
                email="admin@example.com",
                password=make_password("admin"),
                full_name="Administrator",
                role="ADMIN",
                is_active=True,
            )

        admin.username = "admin"
        admin.email = "admin@example.com"
        admin.password = make_password("admin")
        admin.full_name = admin.full_name or "Administrator"
        admin.role = "ADMIN"
        admin.is_active = True
        if created:
            admin.save()
        else:
            admin.save(update_fields=["username", "email", "password", "full_name", "role", "is_active"])

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} default admin account: admin"))
