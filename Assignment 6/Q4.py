# Q4. Vehicle Rental System - Inheritance

class Vehicle:
    def __init__(self, brand, model, daily_rate):
        self.brand = brand
        self.model = model
        self.daily_rate = daily_rate

    def calculate_rent(self, days):
        if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
            raise ValueError("Rental duration must be a positive whole number of days.")
        return self.daily_rate * days


class Car(Vehicle):
    INSURANCE_FEE = 1000

    def calculate_rent(self, days):
        base_rent = super().calculate_rent(days)
        return base_rent + self.INSURANCE_FEE


class Bike(Vehicle):
    DISCOUNT_RATE = 0.10

    def calculate_rent(self, days):
        base_rent = super().calculate_rent(days)
        return base_rent * (1 - self.DISCOUNT_RATE)


if __name__ == "__main__":
    car = Car("Toyota", "Corolla", 5000)
    bike = Bike("Honda", "CD 70", 1500)

    for vehicle in (car, bike):
        print(f"{vehicle.brand} {vehicle.model} for 3 days: Rs. {vehicle.calculate_rent(3):.2f}")

    print("\nTesting invalid rental duration:")
    try:
        car.calculate_rent(0)
    except ValueError as error:
        print(error)