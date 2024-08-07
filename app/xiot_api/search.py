from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import Optional
from fastapi import APIRouter, Body, Request, Response
import yaml
import pyodbc
from loguru import logger

router = APIRouter()

# Load configuration from YAML file
with open("../config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Extract source database configuration
source_db_config = config.get("sync", {}).get("source", {})

# Database connection parameters
# host = '10.1.10.3'
# username = 'sn'
# password = 'Empower@67601510'
# database = 'sndb'

host = source_db_config.get('host')
username = source_db_config.get('username')
password = source_db_config.get('password')
database = source_db_config.get('database')
port = source_db_config.get('port')


def get_db_connection():
    """Create a database connection using pyodbc."""
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={source_db_config.get('host', 'localhost')},{source_db_config.get('port', 1433)};"
        f"DATABASE={source_db_config.get('database', 'sndb')};"
        f"UID={source_db_config.get('username', 'sa')};"
        f"PWD={source_db_config.get('password', 'YourStrong!Passw0rd')}"
    )
    return pyodbc.connect(connection_string)


# cors = '*'
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@router.get("/search_sn_details")
async def get_sn_details(code: Optional[str] = Query(None, description="The serial number to search")):
    if not code:
        raise HTTPException(status_code=400, detail="Bad Request: No code provided")
    logger.debug(f"Start searching for serial number: {code}")

    # Connect to the database
    conn = get_db_connection()
    logger.debug(f"Connected to the database using connection string: {conn}")
    cur = conn.cursor()

    sql = "SELECT attribute, old_code, new_code, product_model FROM sn WHERE sn = ?"
    cur.execute(sql, (code,))
    logger.debug(f"Executed SQL query: {sql}")
    tup_data = cur.fetchall()
    if not tup_data:
        logger.debug(f"No serial number found: {code}")
        raise HTTPException(status_code=404, detail="No sn found")

    lis_data = tup_data[0]
    data = lis_data[0] if lis_data[0] else ''
    data = data.split(',')

    default_code = lis_data[2] if lis_data[2] else lis_data[1]
    product_model = lis_data[3] if lis_data[3] else ""

    conn.close()

    return {
        'default_code': default_code,
        'product_model': product_model,
        'info': data,
    }

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)








































