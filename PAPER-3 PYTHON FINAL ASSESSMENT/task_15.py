# Task 15 - Integrated Order Fulfillment System

import json
import os
import sys
import tempfile
import unittest
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


class OrderError(Exception):
    pass


class OutOfStockError(OrderError):
    pass


class OrderPersistenceError(OrderError):
    pass


def _valid_quantity(quantity):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError(f"Quantity must be a positive integer, got {quantity!r}")
    return quantity


class Product:
    def __init__(self, product_id, name, price, stock):
        price = Decimal(str(price))
        if price < 0:
            raise ValueError("Price cannot be negative")
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise ValueError("Stock must be a non-negative integer")
        self.product_id, self.name, self.price, self.stock = product_id, name, price, stock


class Inventory:
    def __init__(self, products=()):
        self._products = {}
        for product in products:
            if product.product_id in self._products:
                raise ValueError(f"Duplicate product id {product.product_id!r}")
            self._products[product.product_id] = product

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, list):
            raise ValueError("Catalog JSON must be a list of products")
        return cls(Product(p["id"], p["name"], p["price"], p["stock"]) for p in raw)

    def get(self, product_id):
        try:
            return self._products[product_id]
        except KeyError:
            raise KeyError(f"Unknown product {product_id!r}") from None

    def stock_of(self, product_id):
        return self.get(product_id).stock

    def _adjust(self, deltas):
        for product_id, delta in deltas.items():
            self._products[product_id].stock += delta


class Cart:
    def __init__(self, inventory):
        self.inventory = inventory
        self.items = {}
        self.discount_percent = Decimal("0")

    def add(self, product_id, quantity):
        _valid_quantity(quantity)
        product = self.inventory.get(product_id)
        wanted = self.items.get(product_id, 0) + quantity
        if wanted > product.stock:
            raise OutOfStockError(
                f"{product_id}: requested {wanted}, only {product.stock} in stock")
        self.items[product_id] = wanted

    def apply_discount(self, percent):
        percent = Decimal(str(percent))
        if not Decimal("0") <= percent <= Decimal("100"):
            raise ValueError("Discount must be between 0 and 100 percent")
        self.discount_percent = percent

    def subtotal(self):
        return sum((self.inventory.get(pid).price * qty for pid, qty in self.items.items()),
                   Decimal("0"))

    def total(self):
        factor = (Decimal("100") - self.discount_percent) / Decimal("100")
        return (self.subtotal() * factor).quantize(CENT, rounding=ROUND_HALF_UP)


class Order:
    def __init__(self, items, subtotal, discount_percent, total):
        self.order_id = "ORD-" + uuid.uuid4().hex[:12].upper()
        self.created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.items = items
        self.subtotal = subtotal
        self.discount_percent = discount_percent
        self.total = total

    def to_dict(self):
        return {"order_id": self.order_id, "created_at": self.created_at,
                "items": self.items, "subtotal": str(self.subtotal.quantize(CENT)),
                "discount_percent": str(self.discount_percent),
                "total": str(self.total)}


def append_order(path, order):
    """Append the order to a JSON list file using an atomic replace."""
    existing = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            existing = json.load(handle)
        if not isinstance(existing, list):
            raise ValueError("Orders file is not a JSON list")
    existing.append(order.to_dict())
    folder = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(existing, handle, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def place_order(cart, orders_path, persist=append_order):
    """Validate everything first, then update stock, then persist.
    If persisting fails the stock changes are rolled back."""
    if not cart.items:
        raise OrderError("Cart is empty")

    inventory = cart.inventory
    for pid, qty in cart.items.items():
        _valid_quantity(qty)
        if qty > inventory.stock_of(pid):
            raise OutOfStockError(f"{pid}: requested {qty}, only {inventory.stock_of(pid)} in stock")

    lines = [{"product_id": pid, "name": inventory.get(pid).name,
              "unit_price": str(inventory.get(pid).price), "quantity": qty}
             for pid, qty in cart.items.items()]
    order = Order(lines, cart.subtotal(), cart.discount_percent, cart.total())

    deltas = {pid: -qty for pid, qty in cart.items.items()}
    inventory._adjust(deltas)
    try:
        persist(orders_path, order)
    except Exception as exc:
        inventory._adjust({pid: -d for pid, d in deltas.items()})
        raise OrderPersistenceError(f"Order not saved, stock restored: {exc}") from exc

    cart.items.clear()
    return order


class OrderSystemTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.orders = os.path.join(self.tmp.name, "orders.json")
        self.inventory = Inventory([Product("P1", "Pen", 100, 5), Product("P2", "Book", "49.99", 2)])

    def tearDown(self):
        self.tmp.cleanup()

    def test_successful_order_with_discount_updates_stock(self):
        cart = Cart(self.inventory)
        cart.add("P1", 2)
        cart.apply_discount(10)
        order = place_order(cart, self.orders)
        self.assertEqual(order.total, Decimal("180.00"))
        self.assertEqual(self.inventory.stock_of("P1"), 3)
        with open(self.orders) as handle:
            self.assertEqual(json.load(handle)[0]["order_id"], order.order_id)

    def test_invalid_quantity_and_out_of_stock_rejected(self):
        cart = Cart(self.inventory)
        for bad in (0, -1, 1.5, True, "2"):
            with self.assertRaises(ValueError):
                cart.add("P1", bad)
        with self.assertRaises(OutOfStockError):
            cart.add("P2", 3)
        self.assertEqual(self.inventory.stock_of("P2"), 2)

    def test_stale_cart_validated_before_any_stock_change(self):
        cart = Cart(self.inventory)
        cart.add("P1", 2)
        cart.add("P2", 2)
        self.inventory.get("P2").stock = 1
        with self.assertRaises(OutOfStockError):
            place_order(cart, self.orders)
        self.assertEqual(self.inventory.stock_of("P1"), 5)
        self.assertFalse(os.path.exists(self.orders))

    def test_rollback_when_persistence_fails(self):
        cart = Cart(self.inventory)
        cart.add("P1", 3)

        def failing_persist(path, order):
            raise OSError("disk full")
        with self.assertRaises(OrderPersistenceError):
            place_order(cart, self.orders, persist=failing_persist)
        self.assertEqual(self.inventory.stock_of("P1"), 5)

    def test_order_ids_are_unique(self):
        ids = set()
        for _ in range(2):
            cart = Cart(self.inventory)
            cart.add("P1", 1)
            ids.add(place_order(cart, self.orders).order_id)
        self.assertEqual(len(ids), 2)

    def test_bad_discount_rejected(self):
        with self.assertRaises(ValueError):
            Cart(self.inventory).apply_discount(150)


def _demo():
    folder = "sample_data"
    os.makedirs(folder, exist_ok=True)
    catalog = os.path.join(folder, "catalog.json")
    with open(catalog, "w") as handle:
        json.dump([{"id": "P1", "name": "Pen", "price": 100, "stock": 5}], handle)
    inventory = Inventory.from_json(catalog)
    cart = Cart(inventory)
    cart.add("P1", 2)
    cart.apply_discount(10)
    order = place_order(cart, os.path.join(folder, "orders.json"))
    print("Order", order.order_id, "total", order.total, "| stock left:", inventory.stock_of("P1"))


if __name__ == "__main__":
    _demo()
    unittest.main(argv=[sys.argv[0], "-v"])