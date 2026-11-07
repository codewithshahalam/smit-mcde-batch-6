# Task 07 - Employee Payroll Engine.
from abc import ABC, abstractmethod


def _non_negative(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be a non-negative number, got {value!r}")
    return value


class Employee(ABC):
    def __init__(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Employee name must be a non-empty string")
        self.name = name.strip()

    @abstractmethod
    def calculate_pay(self):
        """Return pay for the period."""

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


class SalariedEmployee(Employee):
    def __init__(self, name, monthly_salary):
        super().__init__(name)
        self.monthly_salary = _non_negative("monthly_salary", monthly_salary)

    def calculate_pay(self):
        return self.monthly_salary


class HourlyEmployee(Employee):
    OVERTIME_THRESHOLD = 40
    OVERTIME_MULTIPLIER = 1.5

    def __init__(self, name, hourly_rate, hours_worked):
        super().__init__(name)
        self.hourly_rate = _non_negative("hourly_rate", hourly_rate)
        self.hours_worked = _non_negative("hours_worked", hours_worked)

    def calculate_pay(self):
        regular = min(self.hours_worked, self.OVERTIME_THRESHOLD)
        overtime = max(self.hours_worked - self.OVERTIME_THRESHOLD, 0)
        return (regular + overtime * self.OVERTIME_MULTIPLIER) * self.hourly_rate


class CommissionEmployee(Employee):
    def __init__(self, name, base_pay, sales, rate):
        super().__init__(name)
        self.base_pay = _non_negative("base_pay", base_pay)
        self.sales = _non_negative("sales", sales)
        self.rate = _non_negative("rate", rate)
        if self.rate > 1:
            raise ValueError("rate must be between 0 and 1")

    def calculate_pay(self):
        return self.base_pay + self.sales * self.rate


def payroll_summary(employees):
    rows = [(e.name, type(e).__name__, round(e.calculate_pay(), 2)) for e in employees]
    lines = [f"{'Name':<12}{'Type':<22}{'Pay':>12}"]
    lines += [f"{n:<12}{t:<22}{p:>12,.2f}" for n, t, p in rows]
    lines.append(f"{'TOTAL':<34}{sum(p for _, _, p in rows):>12,.2f}")
    return "\n".join(lines)


if __name__ == "__main__":
    staff = [SalariedEmployee("Ayesha", 3000),
             HourlyEmployee("Bilal", 20, 45),
             CommissionEmployee("Hina", 500, 4000, 0.10)]
    print(payroll_summary(staff))
    try:
        Employee("x")
    except TypeError as exc:
        print("Error:", exc)