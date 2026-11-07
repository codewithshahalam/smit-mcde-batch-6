# Task 01 - Nested Transaction Analyzer
from collections import defaultdict
from numbers import Real

REQUIRED_KEYS = ("id", "customer", "category", "amount", "status")


def analyze_transactions(transactions):
    if not isinstance(transactions, (list, tuple)):
        raise TypeError("transactions must be a list of dictionaries")

    seen_ids = set()
    totals = {}
    by_category = {}

    for index, txn in enumerate(transactions):
        if not isinstance(txn, dict):
            raise TypeError(f"Transaction at index {index} must be a dict")
        missing = [k for k in REQUIRED_KEYS if k not in txn]
        if missing:
            raise ValueError(f"Transaction at index {index} missing keys: {missing}")

        txn_id = txn["id"]
        if txn_id in seen_ids:
            raise ValueError(f"Duplicate transaction id: {txn_id!r}")
        seen_ids.add(txn_id)

        customer = txn["customer"]
        totals.setdefault(customer, 0)
        by_category.setdefault(customer, defaultdict(float))

        if str(txn["status"]).strip().lower() != "success":
            continue

        amount = txn["amount"]
        if isinstance(amount, bool) or not isinstance(amount, Real) or amount < 0:
            raise ValueError(f"Invalid amount in transaction {txn_id!r}: {amount!r}")
        totals[customer] += amount
        by_category[customer][txn["category"]] += amount

    ordered = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))

    report = []
    previous_total, previous_rank = None, 0
    for position, (customer, total) in enumerate(ordered, start=1):
        rank = previous_rank if total == previous_total else position
        previous_total, previous_rank = total, rank
        cats = by_category[customer]
        top = min(cats.items(), key=lambda kv: (-kv[1], kv[0]))[0] if cats else None
        report.append({"rank": rank, "customer": customer,
                       "total_spent": total, "top_category": top})
    return report


if __name__ == "__main__":
    data = [
        {"id": 1, "customer": "Ali", "category": "Food", "amount": 500, "status": "success"},
        {"id": 2, "customer": "Ali", "category": "Travel", "amount": 200, "status": "failed"},
        {"id": 3, "customer": "Sara", "category": "Food", "amount": 700, "status": "success"},
        {"id": 4, "customer": "Zain", "category": "Food", "amount": 50, "status": "failed"},
    ]
    for row in analyze_transactions(data):
        print(row)