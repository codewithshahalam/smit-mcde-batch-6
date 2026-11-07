# Task 08 - Cache Decorator with Expiration
import functools
import inspect
import time


def ttl_cache(seconds):

    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds <= 0:
        raise ValueError("seconds must be a positive number")

    def decorator(func):
        signature = inspect.signature(func)
        cache = {}
        stats = {"hits": 0, "misses": 0, "bypassed": 0}

        def make_key(args, kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            parts = []
            for name, value in bound.arguments.items():
                kind = signature.parameters[name].kind
                if kind is inspect.Parameter.VAR_KEYWORD:
                    value = tuple(sorted(value.items()))
                parts.append((name, value))
            key = tuple(parts)
            hash(key)
            return key

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                key = make_key(args, kwargs)
            except TypeError:
                stats["bypassed"] += 1
                return func(*args, **kwargs)

            now = time.monotonic()
            entry = cache.get(key)
            if entry is not None and now - entry[1] < seconds:
                stats["hits"] += 1
                return entry[0]

            stats["misses"] += 1
            result = func(*args, **kwargs)
            cache[key] = (result, time.monotonic())
            return result

        def cache_info():
            return {**stats, "size": len(cache)}

        def cache_clear():
            cache.clear()
            for k in stats:
                stats[k] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorator


if __name__ == "__main__":
    @ttl_cache(0.3)
    def add(x, y):
        return x + y

    add(x=2, y=3)
    add(y=3, x=2)
    add(2, 3)
    print(add.cache_info())
    time.sleep(0.35)
    add(2, 3)
    print(add.cache_info())
    print(add.__name__, "-", add.__doc__)

    @ttl_cache(5)
    def total(items):
        return sum(items)
    print(total([1, 2, 3]), total.cache_info())