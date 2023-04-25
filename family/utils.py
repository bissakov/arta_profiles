import os
import time
from typing import Any, Callable, Dict, Tuple
import dotenv


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
        print(f'Elapsed time: {elapsed_time:.4f} seconds for function {func.__name__}')
        return result

    return wrapper


def get_env_vars() -> Tuple:
    dotenv.load_dotenv()
    base_url, username, password = os.getenv('URL'), os.getenv('USR'), os.getenv('PSW')
    if not bool(base_url and username and password):
        raise ValueError('One of the variables or .env file does not exist')
    return base_url, username, password


def is_valid_iin(iin: str) -> bool:
    return len(iin) == 12 and next((True for c in iin if c.isdigit()), False)


def convert_value(val: str) -> str | int | float:
    if next((True for c in val if c.isalpha()), False):
        return val.strip()
    val = val.replace(' ', '')
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


def get_headers() -> Dict[str, str]:
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

