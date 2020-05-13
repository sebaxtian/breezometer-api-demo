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
import pytz
import os
import tweepy
import requests
import time
import aqi_tweet


# Locations Dataset
locations_data = pd.read_csv(os.path.join('../input', 'locations.csv'))

# Air Quality Dataset
air_quality = pd.read_csv(os.path.join('../output', 'air_quality.csv'))

# Local Datetime
#LOCAL_UTC = datetime.datetime.utcnow().isoformat()
#print(LOCAL_UTC)
#tz_co = pytz.timezone('America/Bogota')
#local_dt = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
#LOCAL_DATETIME = local_dt.astimezone(tz_co).strftime('%Y-%m-%dT%H:%M:%S')
LOCAL_DATETIME = datetime.datetime.utcnow().astimezone(pytz.timezone('America/Bogota')).isoformat()
print(LOCAL_DATETIME)

# BreezoMeter API Request
def breezometer_api_request(LAT, LON):
    URL_BREEZOMETER = "https://api.breezometer.com/air-quality/v2/current-conditions?"
    API_KEY = os.getenv('BREEZOMETER_API_KEY')
    URL_BREEZOMETER += "lat={lat}&lon={lon}&key={api_key}".format(lat=LAT, lon=LON, api_key=API_KEY)
    # Request
    with requests.get(URL_BREEZOMETER) as bm_aq:
        bm_aq = bm_aq.json()
        return bm_aq

def get_text_tweet(aqi_data, lang='eng'):
    # aqi_data = [ID, LABEL, LAT, LON, BM_UTC, AQI, CATEGORY, COLOR]
    ctg_emoji = {
        "Excellent air quality": "🤩",
        "Good air quality": "🙂",
        "Moderate air quality": "😷",
        "Low air quality": "🥵",
        "Poor air quality": "☠️"
    }
    ctg_esp = {
        "Excellent air quality": "Excelente calidad de aire",
        "Good air quality": "Buena calidad de aire",
        "Moderate air quality": "Moderada calidad de aire",
        "Low air quality": "Baja calidad de aire",
        "Poor air quality": "Pobre calidad de aire"
    }
    # Text Tweet
    text_tweet = ".:-_-:. "
    # Spanish
    if lang == 'esp':
        text_tweet += """Condiciones de Calidad del Aire: #{hashlabel} #Colombia
{label}: {category}
Indice de Calidad del Aire: {aqi} -> {emoji}
#Calidad #Aire
Hora Local: {local_datetime}
""".format(hashlabel=aqi_data[1].replace(" ", ""), label=aqi_data[1], category=ctg_esp[aqi_data[6]], aqi=aqi_data[5], emoji=ctg_emoji[aqi_data[6]], local_datetime=LOCAL_DATETIME)
    else:
        # English
        text_tweet += """Air Quality Conditions: #{hashlabel} #Colombia
{label}: {category}
Air Quality Index: {aqi} -> {emoji}
#Air #Quality
Local Datetime: {local_datetime}
""".format(hashlabel=aqi_data[1].replace(" ", ""), label=aqi_data[1], category=aqi_data[6], aqi=aqi_data[5], emoji=ctg_emoji[aqi_data[6]], local_datetime=LOCAL_DATETIME)
    # Return Text Tweet
    return text_tweet

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
        BM_UTC = bm_aq['data']['datetime']
        AQI = bm_aq['data']['indexes']['baqi']['aqi']
        CATEGORY = bm_aq['data']['indexes']['baqi']['category']
        COLOR = bm_aq['data']['indexes']['baqi']['color']
        # Log
        print(LABEL, '->', CATEGORY)
        # There is?
        there_is = air_quality[(air_quality['id'] == ID) & (air_quality['bm_utc'] == BM_UTC)]
        #print(len(there_is.values))
        if len(there_is.values) == 0:
            # Air Quality Data
            aqi_data = [ID, LABEL, LAT, LON, BM_UTC, AQI, CATEGORY, COLOR]
            # Append Air Quality Data
            data_air_quality.append(aqi_data)
            # Filter Random City
            if LABEL == 'Cali':
                # Get Text Tweet ENG
                text_tweet_eng = get_text_tweet(aqi_data)
                #print(text_tweet_eng)
                text_tweet_esp = get_text_tweet(aqi_data, lang='esp')
                #print(text_tweet_esp)
                # Post Text Tweet ENG
                aqi_tweet.post_tweet(text_tweet_eng)
                # Wait
                time.sleep(2)
                # Post Text Tweet ESP
                aqi_tweet.post_tweet(text_tweet_esp)
        # Wait
        time.sleep(2)
    #print(data_air_quality)
    new_air_quality = pd.DataFrame(columns=['id', 'label', 'lat', 'lon', 'bm_utc', 'aqi', 'category', 'color'], data=data_air_quality)
    # Round Lat Lon values and Return
    return air_quality.append(new_air_quality, ignore_index=True).round({'lat': 6, 'lon': 6})

# Get Air Quality Dataframe
air_quality = get_air_quality_dataframe()

# Save dataframe
air_quality.to_csv(os.path.join('../output', 'air_quality.csv'), index=False)
