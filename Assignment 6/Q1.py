# Q1. Student Result Manager - Encapsulation

class Student:
    def __init__(self, name, marks):
        self.name = name                 # Public attribute
        self._marks = 0                  # Protected by convention
        self.__grade = "F"               # Private attribute
        self.set_marks(marks)

    def set_marks(self, marks):
        if not isinstance(marks, (int, float)) or isinstance(marks, bool):
            print("Invalid marks: enter a number from 0 to 100.")
            return False
        if not 0 <= marks <= 100:
            print("Invalid marks: enter a value from 0 to 100.")
            return False

        self._marks = marks
        if marks >= 80:
            self.__grade = "A"
        elif marks >= 60:
            self.__grade = "B"
        elif marks >= 40:
            self.__grade = "C"
        else:
            self.__grade = "F"
        return True

    def get_marks(self):
        return self._marks

    def get_grade(self):
        return self.__grade


if __name__ == "__main__":
    student1 = Student("Ali", 85)
    student2 = Student("Sara", 55)

    print(f"{student1.name}: marks={student1.get_marks()}, grade={student1.get_grade()}")
    print(f"{student2.name}: marks={student2.get_marks()}, grade={student2.get_grade()}")

    print("\nUpdating Ali's marks to 92:")
    student1.set_marks(92)
    print(f"Updated grade: {student1.get_grade()}")

    print("\nTrying an invalid marks update (120):")
    student2.set_marks(120)
    print(f"Sara's marks remain: {student2.get_marks()}")

    print("\nTrying direct access to __grade:")
    try:
        print(student1.__grade)
    except AttributeError as error:
        print(f"AttributeError: {error}")
    print("Explanation: Python name-mangles __grade to _Student__grade; it is not directly available by its original name.")