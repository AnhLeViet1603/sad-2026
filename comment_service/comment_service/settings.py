from common.settings import configure


configure(globals(), "comment_service", "comments", db_kind="postgres")

