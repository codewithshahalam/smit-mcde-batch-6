# Task 03 - Recursive JSON Path Explorer.

def _equal(value, target):
    return isinstance(value, bool) == isinstance(target, bool) and value == target

def find_paths(data, target):

    results = []

    def walk(node, path, active):
        if _equal(node, target):
            results.append(path)
        if isinstance(node, dict):
            if id(node) in active:
                return
            active = active | {id(node)}
            for key, value in node.items():
                child = f"{path}.{key}" if path else str(key)
                walk(value, child, active)
        elif isinstance(node, (list, tuple)):
            if id(node) in active:
                return
            active = active | {id(node)}
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]", active)

    walk(data, "", frozenset())
    return results

if __name__ == "__main__":
    sample = {"a": [{"x": 5}, 5], "b": {"y": 5}}
    print(find_paths(sample, 5))
    print(find_paths({"f": True, "n": 1, "l": [1, True]}, 1))
    print(find_paths({"f": True, "n": 1, "l": [1, True]}, True))