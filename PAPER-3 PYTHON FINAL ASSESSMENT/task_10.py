# Task 10 - CSV Inventory Reconciliation.
import csv
import os


def _parse_int(text):
    try:
        return int(str(text).strip())
    except ValueError:
        return None


def load_inventory(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or {"sku", "name", "quantity"} - set(reader.fieldnames):
            raise ValueError("inventory.csv must have columns: sku,name,quantity")
        items = {}
        for row in reader:
            sku = (row["sku"] or "").strip()
            qty = _parse_int(row["quantity"])
            if not sku or qty is None or qty < 0:
                raise ValueError(f"Invalid inventory row at line {reader.line_num}: {row}")
            if sku in items:
                raise ValueError(f"Duplicate SKU in inventory: {sku}")
            items[sku] = {"name": row["name"], "quantity": qty}
    return items


def reconcile(inventory_path, movements_path, updated_path, rejected_path):
    inventory = load_inventory(inventory_path)
    rejected = []

    with open(movements_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or {"sku", "type", "units"} - set(reader.fieldnames):
            raise ValueError("movements.csv must have columns: sku,type,units")
        for row in reader:
            sku = (row["sku"] or "").strip()
            kind = (row["type"] or "").strip().upper()
            units = _parse_int(row["units"])

            reason = None
            if sku not in inventory:
                reason = "unknown SKU"
            elif kind not in ("IN", "OUT"):
                reason = "invalid movement type"
            elif units is None:
                reason = "units is not an integer"
            elif units <= 0:
                reason = "units must be positive"
            elif kind == "OUT" and inventory[sku]["quantity"] < units:
                reason = "insufficient stock"

            if reason:
                rejected.append({"row": reader.line_num, "sku": row["sku"],
                                 "type": row["type"], "units": row["units"],
                                 "reason": reason})
                continue
            inventory[sku]["quantity"] += units if kind == "IN" else -units

    with open(updated_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sku", "name", "quantity"])
        for sku, item in inventory.items():
            writer.writerow([sku, item["name"], item["quantity"]])

    with open(rejected_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["row", "sku", "type", "units", "reason"])
        writer.writeheader()
        writer.writerows(rejected)
    return inventory, rejected


def create_sample_files(folder):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "inventory.csv"), "w", newline="") as h:
        h.write("sku,name,quantity\nP01,Widget,10\nP02,Gadget,5\n")
    with open(os.path.join(folder, "movements.csv"), "w", newline="") as h:
        h.write("sku,type,units\nP01,OUT,4\nP01,OUT,9\nP01,IN,2\nP99,IN,1\n"
                "P02,SWAP,1\nP02,IN,0\nP02,OUT,-3\nP02,in,3\n")


if __name__ == "__main__":
    folder = "sample_data"
    create_sample_files(folder)
    inv, rej = reconcile(os.path.join(folder, "inventory.csv"),
                         os.path.join(folder, "movements.csv"),
                         "updated_inventory.csv", "rejected_movements.csv")
    print({k: v["quantity"] for k, v in inv.items()})   # P01=8, P02=8
    for r in rej:
        print(r)