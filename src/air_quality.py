# Dotenv
from dotenv import load_dotenv
# Environment Variables
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Dependencies
import pandas as pd
import numpy as np
import datetime
import os
import tweepy
import requests
import time


# Locations Dataset
locations_data = pd.read_csv(os.path.join('../input', 'locations.csv'))

# Air Quality Dataset
air_quality = pd.read_csv(os.path.join('../output', 'air_quality.csv'))

# Datetime Local
LOCAL_UTC = datetime.datetime.utcnow().isoformat()
#print(LOCAL_UTC)

# BreezoMeter API Request
def breezometer_api_request(LAT, LON):
    URL_BREEZOMETER = "https://api.breezometer.com/air-quality/v2/current-conditions?"
    API_KEY = os.getenv('BREEZOMETER_API_KEY')
    URL_BREEZOMETER += "lat={lat}&lon={lon}&key={api_key}".format(lat=LAT, lon=LON, api_key=API_KEY)
    # Request
    with requests.get(URL_BREEZOMETER) as bm_aq:
        bm_aq = bm_aq.json()
        return bm_aq

# Air Quality Dataframe
def get_air_quality_dataframe():
    #print(locations_data.shape[0])
    data_air_quality = []
    for index in range(locations_data.shape[0]):
        #print(index)
        # GET Attributes
        LAT = locations_data.iloc[[index]]['lat'].values[0]
        LON = locations_data.iloc[[index]]['lon'].values[0]
        # Request
        bm_aq = breezometer_api_request(LAT, LON)
        #print(bm_aq)
        # Location Data
        ID = locations_data.iloc[[index]]['id'].values[0]
        LABEL = locations_data.iloc[[index]]['label'].values[0]
        # BreezoMeter Data
        DATETIME = bm_aq['data']['datetime']
        AQI = bm_aq['data']['indexes']['baqi']['aqi']
        CATEGORY = bm_aq['data']['indexes']['baqi']['category']
        COLOR = bm_aq['data']['indexes']['baqi']['color']
        # Append Air Quality Data
        data_air_quality.append([ID, LABEL, LAT, LON, DATETIME, AQI, CATEGORY, COLOR, LOCAL_UTC])
        # Wait
        time.sleep(2)
    #print(data_air_quality)
    new_air_quality = pd.DataFrame(columns=['id', 'label', 'lat', 'lon', 'bm_utc', 'aqi', 'category', 'color', 'local_utc'], data=data_air_quality)
    return air_quality.append(new_air_quality, ignore_index=True)

# Get Air Quality Dataframe
air_quality = get_air_quality_dataframe()

# Save dataframe
air_quality.to_csv(os.path.join('../output', 'air_quality.csv'), index=False)
