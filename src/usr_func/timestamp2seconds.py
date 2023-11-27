"""
Convert timestamp to seconds

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-24
"""


def timestamp2seconds(timestamp: str) -> float:
    """
    Convert the timestamp to seconds.

    Args:
        timestamp: timestamp in the format of "hh:mm:ss:ms"

    Returns:
        seconds: seconds
    """
    h, m, s = timestamp.split(":")
    seconds = int(h) * 3600 + int(m) * 60 + float(s)
    return seconds
