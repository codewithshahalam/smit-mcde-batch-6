# Task 09 - Streaming Log Inspector.
from collections import Counter
from datetime import datetime

TS_FORMAT = "%Y-%m-%d %H:%M:%S"


class LogStats:
    def __init__(self):
        self.total_lines = 0
        self.malformed = 0


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\r\n").split("|", 2)]
    if len(parts) != 3:
        return None
    timestamp, level, message = parts
    if not level:
        return None
    try:
        datetime.strptime(timestamp, TS_FORMAT)
    except ValueError:
        return None
    return timestamp, level, message


def read_errors(path, stats=None):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if stats is not None:
                stats.total_lines = line_number
            if not line.strip():
                continue
            parsed = parse_line(line)
            if parsed is None:
                if stats is not None:
                    stats.malformed += 1
                continue
            timestamp, level, message = parsed
            if level == "ERROR":
                yield line_number, timestamp, message


def summarize_errors(path):
    stats = LogStats()
    by_date = Counter()
    for _, timestamp, _ in read_errors(path, stats):
        by_date[timestamp[:10]] += 1
    return {"errors_by_date": dict(sorted(by_date.items())),
            "total_errors": sum(by_date.values()),
            "malformed_lines": stats.malformed,
            "total_lines": stats.total_lines}


def create_sample_log(path):
    lines = [
        "2026-11-07 10:30:00 | ERROR | Connection lost",
        "2026-11-07 10:31:12 | INFO | Reconnected",
        "this line is garbage",
        "2026-11-07 11:00:00 | ERROR | Disk almost full | threshold 95%",
        "2026-13-45 99:00:00 | ERROR | Bad timestamp",
        "",
        "2026-11-08 09:15:30 | WARNING | High latency",
        "2026-11-08 09:20:00 | ERROR | Timeout",
    ]
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    import os
    os.makedirs("sample_data", exist_ok=True)
    log_path = os.path.join("sample_data", "app.log")
    create_sample_log(log_path)
    for record in read_errors(log_path):
        print(record)
    print(summarize_errors(log_path))