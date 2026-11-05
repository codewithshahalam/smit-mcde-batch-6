# Q2. Secure Bank Account - Encapsulation

class BankAccount:
    def __init__(self, account_holder, pin, opening_balance=0):
        self.account_holder = account_holder
        self.__pin = str(pin)
        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative.")
        self.__balance = opening_balance

    def deposit(self, amount):
        if amount <= 0:
            print("Deposit rejected: amount must be positive.")
            return False
        self.__balance += amount
        print(f"Deposit successful: Rs. {amount:.2f}")
        return True

    def withdraw(self, amount, pin):
        if str(pin) != self.__pin:
            print("Withdrawal rejected: incorrect PIN.")
            return False
        if amount <= 0:
            print("Withdrawal rejected: amount must be positive.")
            return False
        if amount > self.__balance:
            print("Withdrawal rejected: insufficient balance.")
            return False
        self.__balance -= amount
        print(f"Withdrawal successful: Rs. {amount:.2f}")
        return True

    def get_balance(self, pin):
        if str(pin) != self.__pin:
            print("Balance access rejected: incorrect PIN.")
            return None
        return self.__balance


if __name__ == "__main__":
    account1 = BankAccount("Ahmed", "1234", 5000)
    account2 = BankAccount("Ayesha", "5678", 2500)

    account1.deposit(1500)                 # Successful deposit
    account1.withdraw(2000, "1234")        # Successful withdrawal
    account1.withdraw(10000, "1234")       # Rejected: insufficient balance
    account2.withdraw(500, "0000")         # Rejected: incorrect PIN

    print(f"Ahmed's balance: Rs. {account1.get_balance('1234'):.2f}")
    print(f"Ayesha's balance: Rs. {account2.get_balance('5678'):.2f}")

    print("\nExplanation: Double underscores trigger name mangling, not encryption or access control. Determined code can still access _BankAccount__balance, so this is not true security.")