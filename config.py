import os

LOG_FILE_NAME: str = os.getenv('REC_LOG_FILE_NAME', '')
POSTGRESQL_CONNECTION_STRING: str = os.getenv(
    'REC_POSTGRESQL_CONNECTION_STRING',
    'postgresql+psycopg2://user:pass@localhost:port/db_name'
)

DEBUG: bool = os.getenv('PRESS_DEBUG', "0") == "1"
