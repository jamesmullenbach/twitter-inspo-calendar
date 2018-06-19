"""
    Scrape all the plain text tweets of a (public) user, script version!
"""
import argparse
import html.parser as hparser
import json
import re

import tweepy

def load_keys(key_file):
    d = json.load(open(key_file, 'r'))
    return d['api_key'],d['api_secret'],d['token'],d['token_secret']

def get_tweets(api, root_user):
    tweets = set()
    print("sending initial request...")
    results, oldest_id = retrieve_tweets(api, root_user)
    tweets.update(results)
    
    #now, go back through the remaining history
    while len(results) > 0:
        print("tweets so far: %d. sending request..." % len(tweets))
        results, oldest_id = retrieve_tweets(api, root_user, max_id=oldest_id-1)
        tweets.update(results)

    print("total tweets: %d" % len(tweets))
    return tweets

def retrieve_tweets(api, root_user, max_id=None):
    tweets = []
    results = api.user_timeline(id=root_user, count=200, max_id=max_id)
    for result in results:
        #exclude tweets with media
        if 'media' not in result.entities:
            #exclude replies and RTs (RTs fall under user mentions), tweets with links, and unpopular tweets
            if len(result.entities['user_mentions']) == 0 and len(result.entities['urls']) == 0 and result.favorite_count > 30:
                #get rid of some artifacts and put all tweets on one line
                tweets.append(re.sub('\s+', ' ', hparser.unescape(result.text)))
    oldest_id = results[-1].id if len(results) > 0 else None
    return set(tweets), oldest_id

def write_to_file(data, output_file):
    with open(output_file, 'w') as outfile:
        for tweet in data:
            outfile.write(tweet + "\n")

def main(args):
    KEY_FILE = 'keys.json'

    ROOT_USER = args.user

    api_key, api_secret, token, token_secret = load_keys(KEY_FILE)

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)

    tweets = get_tweets(api, ROOT_USER)

    write_to_file(tweets, args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("user", type=str, help="Username to scrape tweets from (i.e. CodeWisdom or UnixToolTip")
    parser.add_argument("outfile", type=str, help="where to save tweets")
    args = parser.parse_args()
    main(args)

