import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import time
import random


load_dotenv()

token = os.getenv('NEMO_TOKEN')

headers = {

    "Authorization": f"Token {token}"

}
def furnacePush(sensorId, value):

    data = {

        "created_date": datetime.now(timezone(timedelta(hours=-7))).isoformat(),

        "value":   value, 

        "sensor": sensorId

    }

 

    # API endpoint

    url = "https://nemo-dev.stanford.edu/api/sensors/sensor_data/"
    

    # Send the data as JSON
    try:
        response = requests.post(url, json=data, headers=headers)
    except Exception as e:
        print("ISSUE WITH CALLING SERVER, RETURNING CONTROL TO CALLER")
        return
        
    if not response.ok:
        print("ISSUE ON NEMO'S END (IF [404] CHECK url), RETURNING CONTROL TO CALLER")
        return
    else:
        print(f"""FURNACE STATUS SENT AND RECEIVED <{response.status_code}>""")
        print(response.json())
        

   
