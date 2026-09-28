import re
from datetime import timedelta

def parse_duration(duration: str) -> timedelta:
    pattern = r"(\d+)\s*(d|h|m|s)"

    matches = re.findall(pattern, duration.lower())

    if not matches:
        raise ValueError("Invalid duration")

    total = timedelta()

    for value, unit in matches:
        value = int(value)

        if unit == "d":
            total += timedelta(days=value)
        elif unit == "h":
            total += timedelta(hours=value)
        elif unit == "m":
            total += timedelta(minutes=value)
        elif unit == "s":
            total += timedelta(seconds=value)

    return total