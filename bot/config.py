from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
load_dotenv(verbose=True)
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

TG_TOKEN = os.getenv('TG_TOKEN')
PROXY = os.getenv('PROXY')
WEATHER_APP_ID = os.getenv('WEATHER_APP_ID')
CITY = 'Moscow'

__all__ = [
  'TG_TOKEN',
  'PROXY',
  'WEATHER_APP_ID',
  'CITY'
]