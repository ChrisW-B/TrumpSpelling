#!/usr/bin/env python

import tweepy
import config
import re
import sys
import time
import thread
from imp import reload

wordlist = "wordlist.txt"
trumpId = '25073877'
reload(sys)
#twitter doesn't get along with ascii
sys.setdefaultencoding('utf8')


class TrumpListener(tweepy.StreamListener):
    def on_status(self, status):
        print("Got Trump Tweet: " + status.text)
        words = get_words(status.text)
        numMisspelled = count_misspelled(words)
        link = create_link(status)
        newTweet = "This @{:s} tweet stats: {:d} misspelled words found, {:.2f}% accuracy \n {:s}".format(
            status.author.screen_name, int(numMisspelled),
            (1 - float(numMisspelled)/float(len(words))) * 100.0, link)
        print(newTweet)
        api.update_status(newTweet, status.id_str)

    def on_error(self, status_code):
        print(status_code)


def get_words(tweet):
    # creates an array of syllables out of a tweet
    # to be checked for haikus
    stripUrl = re.sub(r"http\S+", "", tweet)
    stripMentions = re.sub(r"@\S+", "", stripUrl)
    stripTags = re.sub(r"#\S+", "", stripMentions)
    stripRTs = stripTags.replace("RT", "")
    tweetArray = re.findall(r"[\w']+", stripRTs)
    return tweetArray


def count_misspelled(wordArray):
    # tries to find words not in dictionary and count them
    numNotFound = 0
    for word in wordArray:
        if find_word(word) == -1:
            numNotFound += 1
    return numNotFound


def find_word(word):
    # searches for word in dictionary file
    word = word.lower() + '\n'
    with open(wordlist, 'r') as dictionary:
        for line in dictionary:
            if word == line:
                    return line
    return -1


def create_link(status):
    # https://twitter.com/realDonaldTrump/status/769539271678013440
    id_str = status.id_str
    author = status.author.screen_name
    link = "https://twitter.com/{}/status/{}/".format(author, str(id_str))
    return link


def limit_handled(cursor):
    # handles twitter limiting and tries to find people
    # who follow
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15*60)


def already_following(user):
    friendship = api.show_friendship(target_id=user.id)
    return friendship[0].following


def follow_back():
    #teamfollowback!
    while True:
        print("starting follow")
        for follower in limit_handled(tweepy.Cursor(api.followers).items()):
            # don't repeatedly follow, and maybe keep out the spammers
            if (not already_following(follower)
                and (
                    follower.friends_count/follower.followers_count < 3 or
                    follower.friends_count < 200
                    )):
                follower.follow()
                print("following " + follower.screen_name)
        time.sleep(15*60)


def user_listener():
    while True:
        try:
            # For accounts bot is following
            print("starting user")
            trumpListener = TrumpListener()
            trumpStream = tweepy.Stream(auth=api.auth, listener=trumpListener)
            trumpStream.filter(follow=[trumpId])
        except Exception as e:
            print(e)
            continue


def setup_threads():
    # set up streams
    thread.start_new_thread(user_listener, ())
    # start follow back
    thread.start_new_thread(follow_back, ())

#authorize tweepy
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
setup_threads()
api.update_status("@ChrisW_B I'm ready!")

while True:
    #Keep the main thread alive so threads stay up
    time.sleep(1)


