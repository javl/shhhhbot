#!/usr/bin/env python
# encoding: utf-8

try:
    # get credentials from credentials.py
    from credentials import consumer_key, consumer_secret, access_token, access_token_secret

except:
    print "Error loading credentials.py. See credentials.example.py"
    exit()

import tweepy, argparse, math, sys, os
from datetime import datetime
import sqlite3 as lite
from argparse import RawTextHelpFormatter

PARSER = argparse.ArgumentParser(prog='nawscraper', description='''Twitter NAW scraper''',
formatter_class=RawTextHelpFormatter)

PARSER.add_argument('-d', dest="drop_database", action='store_true',\
help="Drop the database.")
PARSER.add_argument('-v', dest="verbose", action='count',\
help="Verbose; can be used up to 3 times to set the verbose level.")
PARSER.add_argument('--version', action='version', version='%(prog)s version 1.1',\
help="Show program's version number and exit")
ARGS = PARSER.parse_args()

con = lite.connect('/home/javl/twitterbots/shhhhbot/info.sqlite')
with con:
    cur = con.cursor()

    if ARGS.drop_database:
        if raw_input("Drop the database? (y/n) [n] ") == 'y':
            cur.execute('DROP TABLE IF EXISTS checks')
    cur.execute('CREATE TABLE IF NOT EXISTS "main"."checks" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "since_id" INTEGER)')
    #cur.execute('INSERT INTO "main"."checks" ("since_id") VALUES (?)', (0,))

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

cur.execute("SELECT since_id FROM checks LIMIT 1")
try:
	since_id = cur.fetchone()[0]
except:
	since_id = 0

if ARGS.verbose > 0:
    print "since: ", since_id

def check_rate_limit():
    rate_limit = api.rate_limit_status()

    limit_hit = False

    el = rate_limit['resources']['search']['/search/tweets']
    if ARGS.verbose > 0:
        print "search/tweets:          {}/{}".format(el['remaining'], el['limit'])

    tdelta = datetime.now() - datetime.fromtimestamp(el['reset'])
    tdelta = int(math.ceil(tdelta.total_seconds()/60))
    if el['remaining'] == 0:
        if ARGS.verbose > 0:
            print "reset in {} minutes".format(tdelta)
        limit_hit = True

    el = rate_limit['resources']['statuses']['/statuses/user_timeline']
    if ARGS.verbose > 0:
        print "statuses/user_timeline: {}/{}".format(el['remaining'], el['limit'])

    tdelta = datetime.fromtimestamp(el['reset']) - datetime.now()
    tdelta = int(math.ceil(tdelta.total_seconds()/60))
    if el['remaining'] == 0:
        if ARGS.verbose > 0:
            print "reset in {} minutes".format(tdelta)
        limit_hit = True


    el = rate_limit['resources']['statuses']['/statuses/show/:id']
    if ARGS.verbose > 0:
        print "statuses/show:          {}/{}".format(el['remaining'], el['limit'])
    tdelta = datetime.now() - datetime.fromtimestamp(el['reset'])
    tdelta = int(math.ceil(tdelta.total_seconds()/60))
    if el['remaining'] == 0:
        if ARGS.verbose > 0:
            print "reset in {} minutes".format(tdelta)
        limit_hit = True

    if limit_hit:
        if ARGS.verbose > 0:
            print "Waiting for rate limit to clear."
        exit()



check_rate_limit()

if ARGS.verbose > 0:
    print "================================"

# some words that are often used by bots and we want to ignore
ignore_words = ["sensei", "kale"]
# some words to ignore in the username or user description
ignore_userdata = ["bot"]

#since_id = 888300813889802240
# Find tweets with the sentence, excluding retweets, excluding unsafe tweets
results = api.search(q="but \"tell anyone\" don't OR dont -filter:retweets filter:safe", count=50, result_type="recent", since_id=since_id, include_entities=False)
last_id = None
if ARGS.verbose > 0: print "Number of possible tweets to use: ", len(results)

for tweet in reversed(results):
    # skip tweets containing certain keywords
    try:
        if any(word in tweet.text for word in ignore_words):
            if ARGS.verbose > 0:
                print "==========================="
                print "Skip because of keywords: "
                print tweet.text
                print "==========================="
            continue
    except:
        continue

    # skip tweets by users with certain keywords in name or bio
    try:
        if any(word in (tweet.user.name+tweet.user.description) for word in ignore_userdata):
            if ARGS.verbose > 0:
                print "==========================="
                print "Skip, ignore_userdata in name"
                print tweet.user.name, ", ", tweet.user.description
                print "==========================="
            continue;
    except AttributeError:
        # means this data does not exist, so we can passs
        pass
    except Exception, e: #not sure when we'll hit this
        print "exception on ignore_userdata 1"
        continue

    if ARGS.verbose > 0:
        print "selected tweet from",tweet.user.name
        print tweet.text
        break

    try:
        api.retweet(tweet.id)
        last_id = tweet.id
        break
    except:
        pass

if last_id !=  None:
    with con:
        cur.execute("UPDATE checks SET since_id=?", (last_id,))