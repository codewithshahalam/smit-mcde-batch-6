# Task 02 - Longest Valid Window

def longest_unique_window(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    last_seen = {}
    left = 0
    best_start, best_len = 0, 0
    for right, ch in enumerate(text):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        length = right - left + 1
        if length > best_len:
            best_start, best_len = left, length
    return text[best_start:best_start + best_len], best_start, best_len


if __name__ == "__main__":
    for s in ["abcabcbb", "", "bbbbb", "pwwkew", "a b!a b", "abcdef"]:
        print(repr(s), "->", longest_unique_window(s))