import tweepy
import time
import re
import urllib.request
import ssl
import json


ssl._create_default_https_context = ssl._create_unverified_context


CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

lc_api_key = ""

FILE_NAME = 'last_seen_id.txt'

map = [
    {"name": {"append": " 24-hour activity: "}},
    {"price": {"prepend": "Price: ", "append": " "}},
    {"percent_change_24h": {"append": "% "}},
    {"galaxy_score": {"prepend": "Galaxy Score™ ", "append": " out of 100 "}},
    {"alt_rank": {"prepend": "AltRank™ ", "append": " "}},
    {"social_volume": {"append": " social posts "}},
    {"social_contributors_calc_24h": {"append": " social contributors "}},
    {"social_dominance_calc_24h": {"append": "% social dominance "}},
    {"url_shares_calc_24h": {"append": " shared links "}},
    {"symbol": {"prepend": "$", "append": " "}},
    {"name": {"prepend": "#"}},
]


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def final_render(value, key, asset):
    rendered_tweet = str(asset[0][key])
    if("prepend" in value):
        rendered_tweet = value['prepend'] + rendered_tweet
    if("append" in value):
        rendered_tweet = rendered_tweet + value['append']

    return rendered_tweet


def lunarcrush(Sticker):
    # Get rid of the $ sign as it breaks LC
    ticker = Sticker.replace("$", "")

    url = "https://api.lunarcrush.com/v2?data=assets&key=" + \
        lc_api_key + "&symbol=" + ticker
    asset = json.loads(urllib.request.urlopen(url).read())

    tweet = ""
    for field in map:
        key = list(field.keys())[0]
        value = list(field.values())[0]
        rendered_tweet = final_render(value, key, asset['data'])
        tweet += rendered_tweet
    return tweet


def process_tweet(mention):
    tweet = ""
    if '$' in mention.full_text:
        tickers = re.findall(r'[$][A-Za-z][\S]*', mention.full_text)
        tweet = lunarcrush(tickers[0])
    return tweet


def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)

    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(
        last_seen_id,
        tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        tweet = process_tweet(mention)
        last_seen_id = mention.id
        if tweet is not "":
            api.update_status('@' + mention.user.screen_name +
                              ' @bothersome ' + tweet, mention.id)
        store_last_seen_id(last_seen_id, FILE_NAME)
    

while True:
    reply_to_tweets()
    time.sleep(15)
