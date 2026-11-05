# Q6. Checkout Discount Calculator - Polymorphism

class RegularCustomer:
    DISCOUNT_RATE = 0.05

    def final_price(self, amount):
        _validate_amount(amount)
        return amount * (1 - self.DISCOUNT_RATE)


class PremiumCustomer:
    DISCOUNT_RATE = 0.10

    def final_price(self, amount):
        _validate_amount(amount)
        return amount * (1 - self.DISCOUNT_RATE)


class VIPCustomer:
    DISCOUNT_RATE = 0.20

    def final_price(self, amount):
        _validate_amount(amount)
        return amount * (1 - self.DISCOUNT_RATE)


class GoldCustomer:
    DISCOUNT_RATE = 0.15

    def final_price(self, amount):
        _validate_amount(amount)
        return amount * (1 - self.DISCOUNT_RATE)


def _validate_amount(amount):
    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount < 0:
        raise ValueError("Bill amount must be a non-negative number.")


def print_receipt(customer, amount):
    final_amount = customer.final_price(amount)
    print(f"{customer.__class__.__name__}:")
    print(f"  Original bill: Rs. {amount:,.2f}")
    print(f"  Final amount:  Rs. {final_amount:,.2f}")


if __name__ == "__main__":
    bill = 10000
    customers = [
        RegularCustomer(),
        PremiumCustomer(),
        VIPCustomer(),
        GoldCustomer()
    ]

    for customer in customers:
        print_receipt(customer, bill)

    print("\nTesting a negative bill:")
    try:
        print_receipt(RegularCustomer(), -500)
    except ValueError as error:
        print(error)

    print("\nGoldCustomer was added without changing print_receipt().")