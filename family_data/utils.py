import time
from typing import Dict, Any, Callable


def get_headers() -> Dict:
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator function that measures the time it takes for another function to execute.
    Args:
        func (function): The function to be timed.
    Returns:
        function: A wrapper function that measures the elapsed time.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f'Elapsed time: {elapsed_time:.4f} seconds')
        return result

    return wrapper
