"""
Timer utility module
"""
from time import perf_counter


class Timer:
    """
    Timer class for measuring elapsed time in milliseconds. This utility can be used to 
    track the duration of operations, such as API calls or processing steps, to help with 
    performance monitoring and debugging.
    """
    def __init__(self) -> None:
        self._start = perf_counter()

    def elapsed_ms(self) -> int:
        """
        Elapsed time in milliseconds since the timer was started.
        """
        return int((perf_counter() - self._start) * 1000)
