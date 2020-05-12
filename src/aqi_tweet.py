# Dotenv
from dotenv import load_dotenv
# Environment Variables
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Dependencies
import datetime
import os
import tweepy


# Post Tweet
def post_tweet(text_tweet):
    # Authentication
    auth = tweepy.OAuthHandler(os.getenv('TW_BMAD_CONSUMER_KEY'), os.getenv('TW_BMAD_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('TW_BMAD_ACCESS_TOKEN'), os.getenv('TW_BMAD_ACCESS_TOKEN_SECRET'))
    # Tweepy API Object
    api = tweepy.API(auth)
    # Send Tweet
    api.update_status(text_tweet)
