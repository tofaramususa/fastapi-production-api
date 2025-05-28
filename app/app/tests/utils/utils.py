import random
import string
from typing import Optional


def random_lower_string(length: Optional[int] = 32) -> str:
    """
    Generate a random lowercase string of specified length.

    Args:
        length: The length of the string to generate. Defaults to 32.

    Returns:
        A random string containing only lowercase letters.
    """
    return "".join(random.choices(string.ascii_lowercase, k=length))
