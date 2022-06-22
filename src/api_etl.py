from dataclasses import dataclass
from datetime import datetime as dt
import logging
import sys
from typing import Any, Dict, List, Optional
import psycopg2 as p
import psycopg2.extras as pe
import requests

#this utility script with DB credentials is not included for obvious reasons.
#it contains only a small class used to store the necessary DB login details.
from utils.games_savings_creds import CredsStore


#this function calls the 'stores' endpoint of the CheapShark API
#and pulls updated statuses for all the vendors they track
def stores_endpoint_call() -> List[Dict[str, Any]]:
    url ="https://www.cheapshark.com/api/1.0/stores"
    try:
        response = requests.get(url)
    except requests.ConnectionError as ce:
        logging.error(f"There was an error with the request, {ce}")
        sys.exit(1)
    return response


#this function extracts the bulk of data used by the dashboard
#worth noting games and deals have a one-to-many relationship
def deals_endpoint_call(page_number) -> List[Dict[str, Any]]:
    params = {"pageNumber": page_number, "sortBy": "savings"}
    url ="https://www.cheapshark.com/api/1.0/deals"
    try:
        response = requests.get(url, params = params)
    except requests.ConnectionError as ce:
        logging.error(f"There was an error with the request, {ce}")
        sys.exit(1)
    return response


#these two functions provide the SQL strings that are used to insert
#the stores and deals data into the postgres db on RDS. The formatting
#is per psycopg2's way of passing parameters into SQL queries
def stores_insert_query() -> str:
    return '''
    INSERT INTO games_savings.stores (
        store_id,
        store_name,
        is_active,
        updated_timestamp
    )
    VALUES (
        %(storeID)s,
        %(storeName)s,
        %(isActive)s,
        %(updated_timestamp)s
    );
    '''

def deals_insert_query() -> str:
    return '''
    INSERT INTO games_savings.deals (
        title,
        store_id,
        game_id,
        sale_price,
        normal_price,
        is_on_sale,
        savings,
        metacritic_score,
        steam_rating_percent,
        release_date,
        last_change,
        deal_rating,
        deal_url,
        updated_timestamp
    )
    VALUES (
        %(title)s,
        %(storeID)s,
        %(gameID)s,
        %(salePrice)s,
        %(normalPrice)s,
        %(isOnSale)s,
        %(savings)s,
        %(metacriticScore)s,
        %(steamRatingPercent)s,
        %(releaseDate)s,
        %(lastChange)s,
        %(dealRating)s,
        %(dealURL)s,
        %(updated_timestamp)s
    );
    '''

#given how simple the overall app is at the moment,
#there's no reason not to keep data clean-up simple as well
def db_truncate(table_name:str, cursor):
    cursor.execute(f"TRUNCATE {table_name};")

creds = CredsStore()

conn = p.connect(
host = creds.host,
port = creds.port,
database = creds.database,
user = creds.user,
password = creds.password
)

cur = conn.cursor()



def run_stores_etl() -> None:
    data = stores_endpoint_call().json()

    for r in data:
        r["updated_timestamp"] = dt.now()
    db_truncate("games_savings.stores", cur)
    pe.execute_batch(cur,stores_insert_query(),data)
    conn.commit()


def run_deals_etl() -> List[str]:
    data = []
    status_code = 200
    page_number = 0

    #runs a fresh request against the endpoint (with a new page number)
    #as long as the previous request returned successfully
    while status_code == 200:
        response = deals_endpoint_call(page_number)
        page_number+=1
        status_code = response.status_code
        if status_code == 200:
            data.extend(response.json())

    for r in data:
        r["updated_timestamp"] = dt.now()
        #converting the UTC timestamps to python datetimes so they play nice with psycopg2
        r["releaseDate"] = dt.fromtimestamp(r["releaseDate"])
        r["lastChange"] = dt.fromtimestamp(r["lastChange"])
        r["dealURL"] = "https://www.cheapshark.com/redirect?dealID=" + r["dealID"]

    #the data is small enough (~3000-6000 rows) that it makes sense to 
    #maintain idempotency by deleting and re-acquiring all the data each run
    db_truncate("games_savings.deals", cur)
    pe.execute_batch(cur,deals_insert_query(),data)
    conn.commit()

if __name__ == "__main__":

    run_stores_etl()
    run_deals_etl()