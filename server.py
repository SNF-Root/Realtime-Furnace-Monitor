import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import time
import random


headers = {

    "Content-Type": "application/json"

}
def furnacePush(sensorId, value):

    data = {

        "created_date": datetime.now(timezone(timedelta(hours=-7))).isoformat(),

        "value":   value, 

        "sensor": sensorId

    }

 

    # API endpoint

    url = "http://192.168.140.146:8000/esp/receive_send"
    

    # Send the data as JSON
    try:
        response = requests.post(url, json=data, headers=headers)
    except Exception as e:
        print(str(e))

    print(response.json())

    print(response.status_code)


   
returnCode = furnacePush(15, 10)
print(returnCode)