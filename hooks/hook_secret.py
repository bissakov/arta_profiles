import os
import dotenv


def get_env(env_name: str) -> str:
    return env if (env := os.getenv(env_name)) else ''


dotenv.load_dotenv()
os.environ['URL'] = get_env('URL') 
os.environ['USR'] = get_env('USR')
os.environ['PSW'] = get_env('PSW')

