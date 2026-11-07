# Task 06 - Banking Ledger with OOP
import itertools
from dataclasses import dataclass
from decimal import Decimal

_txn_ids = itertools.count(1)
_CENT = Decimal("0.01")


def _money(value, *, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise ValueError(f"Invalid amount: {value!r}")
    try:
        amount = Decimal(str(value))
    except Exception:
        raise ValueError(f"Invalid amount: {value!r}") from None
    if not amount.is_finite():
        raise ValueError("Amount must be finite")
    if amount != amount.quantize(_CENT):
        raise ValueError("Amount cannot have more than 2 decimal places")
    if amount < 0 or (amount == 0 and not allow_zero):
        raise ValueError("Amount must be positive")
    return amount


@dataclass(frozen=True)
class Transaction:
    txn_id: int
    action: str
    amount: Decimal
    balance_after: Decimal


class InsufficientFundsError(Exception):
    pass

class AccountNotFoundError(KeyError):
    pass


class Account:
    def __init__(self, account_id, owner, opening_balance=0):
        self._id = account_id
        self._owner = owner
        self._balance = Decimal("0")
        self._history = []
        opening = _money(opening_balance, allow_zero=True)
        if opening > 0:
            self._balance = opening
            self._record("open", opening)

    @property
    def account_id(self):
        return self._id

    @property
    def owner(self):
        return self._owner

    @property
    def balance(self):
        return self._balance

    @property
    def history(self):
        return tuple(self._history)

    def _record(self, action, amount):
        txn = Transaction(next(_txn_ids), action, amount, self._balance)
        self._history.append(txn)
        return txn

    def can_withdraw(self, amount):
        return self._balance >= amount

    def deposit(self, amount, action="deposit"):
        amount = _money(amount)
        self._balance += amount
        return self._record(action, amount)

    def withdraw(self, amount, action="withdrawal"):
        amount = _money(amount)
        if not self.can_withdraw(amount):
            raise InsufficientFundsError(
                f"Account {self._id}: balance {self._balance} < {amount}")
        self._balance -= amount
        return self._record(action, amount)

    def statement(self):
        lines = [f"Statement for {self._owner} (account {self._id})",
                 f"{'ID':>4}  {'Action':<13}{'Amount':>12}{'Balance':>12}"]
        for t in self._history:
            lines.append(f"{t.txn_id:>4}  {t.action:<13}{t.amount:>12}{t.balance_after:>12}")
        lines.append(f"Closing balance: {self._balance}")
        return "\n".join(lines)


class Bank:
    def __init__(self):
        self._accounts = {}

    def open_account(self, account_id, owner, opening_balance=0):
        if account_id in self._accounts:
            raise ValueError(f"Account {account_id!r} already exists")
        account = Account(account_id, owner, opening_balance)
        self._accounts[account_id] = account
        return account

    def get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError:
            raise AccountNotFoundError(f"Account {account_id!r} does not exist") from None

    def deposit(self, account_id, amount):
        return self.get(account_id).deposit(amount)

    def withdraw(self, account_id, amount):
        return self.get(account_id).withdraw(amount)

    def transfer(self, from_id, to_id, amount):
        """Atomic: everything is validated before any balance changes."""
        source, target = self.get(from_id), self.get(to_id)
        if source is target:
            raise ValueError("Cannot transfer to the same account")
        amount = _money(amount)
        if not source.can_withdraw(amount):
            raise InsufficientFundsError(
                f"Account {from_id}: balance {source.balance} < {amount}")
        out = source.withdraw(amount, action=f"transfer->{to_id}")
        inc = target.deposit(amount, action=f"transfer<-{from_id}")
        return out, inc


if __name__ == "__main__":
    bank = Bank()
    bank.open_account("A", "Ali", 1000)
    bank.open_account("B", "Sara", 200)
    bank.transfer("A", "B", 350)
    print(bank.get("A").balance, bank.get("B").balance)
    print(bank.get("A").statement())
    for action in (lambda: bank.transfer("A", "B", 5000),
                   lambda: bank.deposit("A", -5),
                   lambda: bank.transfer("A", "Z", 10)):
        try:
            action()
        except Exception as exc:
            print(type(exc).__name__, "-", exc)
    print(bank.get("A").balance, bank.get("B").balance)