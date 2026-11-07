# Task 12 - Custom Iterable Range Toolkit.

class ReversibleRange:

    def __init__(self, start, stop, step=1):
        for name, value in (("start", start), ("stop", stop), ("step", step)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        if step == 0:
            raise ValueError("step must not be zero")
        self.start, self.stop, self.step = start, stop, step
        if step > 0:
            self._len = max(0, (stop - start + step - 1) // step)
        else:
            self._len = max(0, (start - stop - step - 1) // (-step))

    def __len__(self):
        return self._len

    def __iter__(self):
        value = self.start
        for _ in range(self._len):
            yield value
            value += self.step

    def __reversed__(self):
        value = self.start + (self._len - 1) * self.step
        for _ in range(self._len):
            yield value
            value -= self.step

    def __contains__(self, item):
        if isinstance(item, bool) or not isinstance(item, int):
            return False
        if self.step > 0:
            in_bounds = self.start <= item < self.stop
        else:
            in_bounds = self.stop < item <= self.start
        return in_bounds and (item - self.start) % self.step == 0

    def __repr__(self):
        return f"ReversibleRange({self.start}, {self.stop}, {self.step})"


if __name__ == "__main__":
    r = ReversibleRange(2, 11, 3)
    print(list(r), list(reversed(r)), 5 in r, 6 in r, len(r))
    # Cross-check against built-in range
    import itertools
    for a, b, s in itertools.product(range(-8, 9), range(-8, 9), [-3, -2, -1, 1, 2, 3]):
        mine, ref = ReversibleRange(a, b, s), range(a, b, s)
        assert len(mine) == len(ref)
        assert list(mine) == list(ref)
        assert list(reversed(mine)) == list(reversed(ref))
        assert all((x in mine) == (x in ref) for x in range(-12, 13))
    print("Matches built-in range for all test cases")
    print(list(ReversibleRange(10, 0, -3)), len(ReversibleRange(5, 5)))