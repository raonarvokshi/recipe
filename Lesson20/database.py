import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
Database_url = os.getenv("Database_url")


def get_db_connection():
    connection = sqlite3.connect(Database_url)
    connection.row_factory = sqlite3.Row
    return connection
