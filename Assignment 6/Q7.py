# Q7. Shape Calculator - Abstraction

from abc import ABC, abstractmethod
import math


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass


class Circle(Shape):
    PI = 3.14159

    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("Radius must be positive.")
        self.radius = radius

    def area(self):
        return self.PI * self.radius ** 2

    def perimeter(self):
        return 2 * self.PI * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


if __name__ == "__main__":
    circle = Circle(5)
    rectangle = Rectangle(4, 6)

    print(f"Circle (radius 5) area: {circle.area():.5f}")
    print(f"Circle (radius 5) perimeter: {circle.perimeter():.5f}")
    print(f"Rectangle (4 x 6) area: {rectangle.area():.2f}")
    print(f"Rectangle (4 x 6) perimeter: {rectangle.perimeter():.2f}")

    print("\nTrying to create Shape directly:")
    try:
        shape = Shape()
    except TypeError as error:
        print(f"TypeError: {error}")
    print("Explanation: Shape is abstract and has unimplemented abstract methods, so it cannot be instantiated directly.")