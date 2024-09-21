"""Running DAG from here
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
import requests

# For kafka streams
from kafka import KafkaProducer
import time

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


default_args = {
    'owner': 'airscholar',
    'start_date': datetime(2023, 9, 3, 10, 00)
}


def get_data() -> dict:
    res = requests.get("https://randomuser.me/api/")
    res = res.json()
    res = res['results'][0]
    # print(json.dumps(res, indent=3))
    return res

def format_data(res: dict):
    data = {}
    location = res['location']
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])}  {location['street']['name']} " \
                      f"{location['city']},  {location['state']}, {location['country']}"
    data['postcode'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']
    return data


def stream_data():
    """Get access to API
    """
    res = get_data()
    res = format_data(res)
    print(json.dumps(res, indent=3))

    producer = KafkaProducer(bootstrap_servers=['broker:29092']) # 'localhost:9092' #, max_block_ms=10000)
    # time.sleep(5)
    producer.send('users_created', json.dumps(res).encode('utf-8'))
    # producer.flush()  

# Entry point
with DAG('user_automation', # task id
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False
         ) as dag:
    
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )

stream_data()