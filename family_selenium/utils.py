import os
from typing import Dict, Tuple, Any
import dotenv


def get_env_vars() -> Tuple[str, str, str]:
    dotenv.load_dotenv()
    base_url, username, password = os.getenv('URL'), os.getenv('USR'), os.getenv('PSW')
    if not bool(base_url and username and password):
        raise ValueError('One of the variables or .env file does not exist')
    return base_url, username, password


def is_valid_iin(iin: str) -> bool:
    return len(iin) == 12 and next((True for c in iin if c.isdigit()), False)


def convert_value(val: str) -> Any:
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
