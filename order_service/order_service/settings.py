from common.settings import configure


configure(globals(), "order_service", "orders", db_kind="postgres")

