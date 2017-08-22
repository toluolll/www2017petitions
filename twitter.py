import os
import json
from datetime import datetime, timedelta

# Install the "python-twitter" package from here: https://python-twitter.readthedocs.org/en/latest/installation.html
from twitter import Api

# Fill in your credentials here or set it via environment variables as is the case here
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", None)
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", None)
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", None)
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", None)

# Bounding Box for Lausanne
LAUSANNE_LOCATIONS = ["6.5754736", "46.5045139", "6.720813699999999", "46.60257729999999"]

FOLLOWS = None
TRACK = ["thepetitionsite"]

api = Api(consumer_key=CONSUMER_KEY,
          consumer_secret=CONSUMER_SECRET,
          access_token_key=ACCESS_TOKEN,
          access_token_secret=ACCESS_TOKEN_SECRET,
          use_gzip_compression=False,
          debugHTTP=True)

##
# Helper Functions
##

# User Screen Name
def getScreenName(tweet):
    if tweet.get('user', None) is not None:
        return tweet.get('user').get('screen_name', None)

# Text
def getText(tweet):
    if tweet.get('text', None):
        return tweet.get('text', None).strip()

# Location
def getLocation(tweet):
    longitude = latitude = None

    coordinates = tweet.get('coordinates', None)
    if coordinates is not None:
        longitude = coordinates['coordinates'][0]
        latitude = coordinates['coordinates'][1]

    return tuple([longitude, latitude])

# Hashtags
def getHashtags(tweet):
    hashtags = ''
    if tweet.get('entities', None) is not None:
            if tweet.get('entities', None).get('hashtags', None) is not None:
                hashtagsList = tweet.get('entities', None).get('hashtags', None)

                for hashtagObj in hashtagsList:
                    hashtags += "#" + hashtagObj.get('text', None).strip() + ","

    return hashtags

# Language
def getLang(tweet):
    return tweet.get('lang', None)

def getTime(tweet):
    tweetDate = tweet.get('created_at', None)
    utcOffset = tweet.get('user').get('utc_offset')

    if utcOffset is not None:
        tweetCorrectedDate = datetime.strptime(tweetDate, '%a %b %d %H:%M:%S +0000 %Y') + timedelta(seconds=int(utcOffset))
    else:
        tweetCorrectedDate = datetime.strptime(tweetDate, '%a %b %d %H:%M:%S +0000 %Y')

    return tweetCorrectedDate


# The python-twitter package provides functions to access both the REST and Streaming API.
# In this application, we are using the Streaming API interface. Using the function api.GetStreamFilter
# we are given a generator that yields one tweet at a time as a JSON dictionary
def main():
    with open('output.txt', 'a') as f:
        # Collects hashtags of interest within Lausanne region
        while True:
            try:
                for tweet in api.GetStreamFilter(track=TRACK, stall_warnings=True):
                    user = getScreenName(tweet) # Username
                    text = getText(tweet) # Text # Text
                    creation_time = getTime(tweet) # Time
                    longlat = getLocation(tweet) # Location
                    lang = getLang(tweet) # Language
                    hashtags = getHashtags(tweet) # Hashtags

                    # print(user + " at " + str(creation_time) + " TWEETED: \"" + text + "\" in LANG: " + lang + ", containing HASHTAGS: " + hashtags + os.linesep)

                    # Write the JSON object to disk
                    f.write(json.dumps(tweet) + os.linesep)
            except Exception as e:
                continue

if __name__ == '__main__':
    main()
