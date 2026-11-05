# Q8. Payment Gateway - Abstraction

from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

    @abstractmethod
    def refund(self, amount):
        pass

    @staticmethod
    def validate_amount(amount):
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("Transaction amount must be a positive number.")


class CardPayment(PaymentMethod):
    def pay(self, amount):
        self.validate_amount(amount)
        print(f"Card | Payment | Rs. {amount:,.2f}")

    def refund(self, amount):
        self.validate_amount(amount)
        print(f"Card | Refund | Rs. {amount:,.2f}")


class WalletPayment(PaymentMethod):
    def pay(self, amount):
        self.validate_amount(amount)
        print(f"Wallet | Payment | Rs. {amount:,.2f}")

    def refund(self, amount):
        self.validate_amount(amount)
        print(f"Wallet | Refund | Rs. {amount:,.2f}")


class BankTransferPayment(PaymentMethod):
    def pay(self, amount):
        self.validate_amount(amount)
        print(f"Bank Transfer | Payment | Rs. {amount:,.2f}")

    def refund(self, amount):
        self.validate_amount(amount)
        print(f"Bank Transfer | Refund | Rs. {amount:,.2f}")


def process_transaction(method, amount):
    method.pay(amount)


if __name__ == "__main__":
    card = CardPayment()
    wallet = WalletPayment()
    bank = BankTransferPayment()

    process_transaction(card, 2500)
    process_transaction(wallet, 1200)
    process_transaction(bank, 5000)

    print("\nRefund examples:")
    card.refund(500)
    wallet.refund(200)

    print("\nTesting invalid transaction amount:")
    try:
        process_transaction(card, 0)
    except ValueError as error:
        print(error)

    print("\nA new payment class can implement Payment Method and work with process_transaction() unchanged.")