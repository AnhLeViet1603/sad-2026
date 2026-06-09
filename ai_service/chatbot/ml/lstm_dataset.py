import csv
from collections import defaultdict
from dataclasses import dataclass

from chatbot.models import UserBehavior


EVENT_TYPES = ["VIEWED", "ADDED_TO_CART", "PURCHASED", "RATED"]
PAD_TOKEN = "<PAD>"
UNKNOWN_TOKEN = "<UNK>"


@dataclass
class SequenceDataset:
    product_sequences: list
    event_sequences: list
    targets: list
    product_to_index: dict
    index_to_product: dict
    event_to_index: dict
    sequence_length: int


def load_behavior_rows_from_db(event_type="ADDED_TO_CART"):
    rows = UserBehavior.objects.all().order_by("user_id", "created_at", "id")
    if event_type:
        rows = rows.filter(event_type=event_type)
    return [
        {
            "user_id": behavior.user_id,
            "product_id": behavior.product_id,
            "event_type": behavior.event_type,
            "created_at": behavior.created_at.isoformat(),
        }
        for behavior in rows
    ]


def load_behavior_rows_from_csv(path):
    with open(path, newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def build_sequence_dataset(rows, sequence_length=5, min_events_per_user=3):
    by_user = defaultdict(list)
    for row in rows:
        by_user[int(row["user_id"])].append(
            {
                "product_id": int(row["product_id"]),
                "event_type": row.get("event_type") or "ADDED_TO_CART",
                "created_at": row.get("created_at") or "",
            }
        )

    product_ids = sorted({event["product_id"] for events in by_user.values() for event in events})
    product_to_index = {PAD_TOKEN: 0, UNKNOWN_TOKEN: 1}
    for product_id in product_ids:
        product_to_index[str(product_id)] = len(product_to_index)
    index_to_product = {index: token for token, index in product_to_index.items()}

    event_to_index = {PAD_TOKEN: 0}
    for event_type in EVENT_TYPES:
        event_to_index[event_type] = len(event_to_index)

    product_sequences = []
    event_sequences = []
    targets = []

    for events in by_user.values():
        events = sorted(events, key=lambda item: item["created_at"])
        if len(events) < min_events_per_user:
            continue
        for target_index in range(1, len(events)):
            history = events[max(0, target_index - sequence_length) : target_index]
            padded_history = [{"product_id": 0, "event_type": PAD_TOKEN}] * (sequence_length - len(history)) + history
            product_sequences.append(
                [product_to_index.get(str(item["product_id"]), product_to_index[UNKNOWN_TOKEN]) for item in padded_history]
            )
            event_sequences.append([event_to_index.get(item["event_type"], event_to_index[PAD_TOKEN]) for item in padded_history])
            targets.append(product_to_index[str(events[target_index]["product_id"])])

    return SequenceDataset(
        product_sequences=product_sequences,
        event_sequences=event_sequences,
        targets=targets,
        product_to_index=product_to_index,
        index_to_product=index_to_product,
        event_to_index=event_to_index,
        sequence_length=sequence_length,
    )
