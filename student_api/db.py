# db.py
import pyodbc
import pandas as pd
import numpy as np
import struct
from azure.identity import InteractiveBrowserCredential

from dotenv import load_dotenv
import os

load_dotenv()

SQL_ENDPOINT = os.getenv("SQL_ENDPOINT")
DATABASE = os.getenv("DATABASE")

def get_connection():
    credential = InteractiveBrowserCredential()
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={SQL_ENDPOINT},1433;"
        f"Database={DATABASE};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    conn = pyodbc.connect(conn_str, attrs_before={1256: token_struct})
    return conn

def sanitize(df: pd.DataFrame) -> pd.DataFrame:
    # Replace NaN and Inf with None so json.dumps can serialize them as null
    return df.replace({np.nan: None, np.inf: None, -np.inf: None})

def query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return sanitize(df)