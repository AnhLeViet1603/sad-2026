from django.core.management.base import BaseCommand

from chatbot.models import ProductDocument, UserBehavior
from chatbot.services import neo4j_driver, sync_products_from_service, track_behavior_graph


DEMO_USERS = list(range(1001, 1011))
EVENT_COUNTS = {
    "VIEWED": 80,
    "ADDED_TO_CART": 30,
    "PURCHASED": 30,
    "RATED": 20,
}


class Command(BaseCommand):
    help = "Seed demo UserBehavior rows and Neo4j relationships using supported event types."

    def handle(self, *args, **options):
        synced = sync_products_from_service()
        products = list(ProductDocument.objects.order_by("product_id"))
        if not products:
            self.stdout.write(self.style.WARNING("No products available after sync."))
            return

        UserBehavior.objects.filter(user_id__in=DEMO_USERS).delete()
        self._delete_demo_graph_users()

        created = 0
        for user_index, user_id in enumerate(DEMO_USERS):
            persona_products = self._persona_products(products, user_index)
            created += self._create_events(user_id, persona_products)

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {synced} products and seeded {created} behavior events for {len(DEMO_USERS)} demo users."
            )
        )

    def _persona_products(self, products, user_index):
        window = max(8, min(12, len(products)))
        start = (user_index * 3) % len(products)
        return [products[(start + offset) % len(products)] for offset in range(window)]

    def _create_events(self, user_id, products):
        created = 0
        recipes = [
            ("VIEWED", 8),
            ("ADDED_TO_CART", 3),
            ("PURCHASED", 3),
            ("RATED", 2),
        ]
        for event_type, count in recipes:
            for product in products[:count]:
                UserBehavior.objects.create(
                    user_id=user_id,
                    product_id=product.product_id,
                    event_type=event_type,
                    metadata={"seed": "graph_demo"},
                )
                track_behavior_graph(user_id, product.product_id, event_type)
                created += 1
        return created

    def _delete_demo_graph_users(self):
        driver = neo4j_driver()
        if not driver:
            return
        try:
            with driver.session() as session:
                session.run(
                    """
                    MATCH (u:User)
                    WHERE u.id IN $user_ids
                    DETACH DELETE u
                    """,
                    user_ids=DEMO_USERS,
                )
        finally:
            driver.close()
