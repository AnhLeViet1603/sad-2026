from common.settings import configure


configure(globals(), "payment_service", "payments", db_kind="mysql")

