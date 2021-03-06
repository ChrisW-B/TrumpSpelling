#!/usr/bin/env python

from imp import reload
import tweepy
import config
import re
import sys
import time
import thread
import pickle

wordlist = "wordlist.txt"
savedData = "saved.data"
# my twitter id: 34784570
# trumps id: 25073877
trumpId = '25073877'
reload(sys)
#twitter doesn't get along with ascii
sys.setdefaultencoding('utf8')


class TrumpListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.id_str == trumpId:
            print("Got Trump Tweet: " + status.text)
            words = get_words(status.text)
            numMisspelled = int(count_misspelled(words))
            link = create_link(status)
            accuracy = (1 - float(numMisspelled) / float(len(words))) * 100.0
            overallAcc = get_overall_acc(len(words), numMisspelled)
            newTweet = "This @{:s} tweet stats: {:d}/{:d} misspelled words found, {:.2f}% accuracy. Overall correct: {:.2f}% \n{:s}".format(
                status.author.screen_name, numMisspelled,
                int(len(words)), accuracy, overallAcc, link)
            print(newTweet)
            api.update_status(newTweet, status.id_str)

    def on_error(self, status_code):
        print(status_code)


def get_overall_acc(numWords, numMisspelled):
    fd = open(savedData, 'r+')
    overallData = pickle.load(fd)
    overallData['numWords'] += numWords
    overallData['numMisspelled'] += numMisspelled
    overallAcc = (1 - float(overallData['numMisspelled'])
                  / float(len(overallData['numWords']))) * 100.0
    fd.seek(0)
    pickle.dump(overallData, fd)
    fd.close()
    return overallAcc


def get_words(tweet):
    # creates an array of syllables out of a tweet
    # to be checked for haikus
    stripUrl = re.sub(r"http\S+", "", tweet)
    stripMentions = re.sub(r"@\S+", "", stripUrl)
    stripTags = re.sub(r"#\S+", "", stripMentions)
    stripNums = re.sub(r'\w*\d\w*', '', stripTags).strip()
    stripProperNouns = re.sub(r"(?<![\s\.\!\?]) ([A-Z]([a-z]|[A-Z])+(\')*[a-z]*)", '', stripNums)
    stripAbbrev = re.sub(r"(([A-Z])\.)", '', stripProperNouns)
    stripRTs = stripAbbrev.replace("RT", "")
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


def user_listener():
    while True:
        try:
            # For accounts bot is following
            print("starting user")
            trumpListener = TrumpListener()
            trumpStream = tweepy.Stream(auth=api.auth, listener=trumpListener)
            trumpStream.userstream()
        except Exception as e:
            print(e)
            continue


def setup_threads():
    # set up streams
    thread.start_new_thread(user_listener, ())

#authorize tweepy
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
setup_threads()
api.update_status("@ChrisW_B I'm ready!")

while True:
    #Keep the main thread alive so threads stay up
    time.sleep(1)
