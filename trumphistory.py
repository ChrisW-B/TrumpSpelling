#!/usr/bin/env python
# pulls down all of trumps old tweets for past analysis
from imp import reload
import tweepy
import config
import re
import sys
from collections import Counter

wordlist = "wordlist.txt"
# my twitter id: 34784570
# trumps id: 25073877
trumpId = '25073877'
reload(sys)
#twitter doesn't get along with ascii
sys.setdefaultencoding('utf8')


def read_tweets():
    misspelledWords = []
    numRead = 0
    totalWords = 0
    for page in tweepy.Cursor(api.user_timeline, id=trumpId, count=200).pages():
        print("Read {} tweets".format(numRead))
        for status in page:
            numRead += 1
            words = get_words(status.text)
            misspelled = get_misspelled(words)
            misspelledWords.extend(misspelled)
            totalWords += len(words)
    print("Total words: {} \nTotal misspelled: {}".format(totalWords, len(misspelledWords)))
    return Counter(misspelledWords)


def get_words(tweet):
    # creates an array of syllables out of a tweet
    # to be checked for haikus
    stripUrl = re.sub(r"http\S+", "", tweet)
    stripMentions = re.sub(r"@\S+", "", stripUrl)
    stripTags = re.sub(r"#\S+", "", stripMentions)
    stripNums = re.sub(r'\w*\d\w*', '', stripTags).strip()
    stripProperNouns = re.sub(r"(?<![\s\.\!\?]) ([A-Z]([a-z]|[A-Z])+(\')*[a-z]*)", '', stripNums)
    stripRTs = stripProperNouns.replace("RT", "")

    tweetArray = re.findall(r"[\w']+", stripRTs)
    return tweetArray


def get_misspelled(wordArray):
    # tries to find words not in dictionary and count them
    notFoundWords = []
    for word in wordArray:
        if find_word(word) == -1:
            notFoundWords.append(word)
    print("Couldn't find {}".format(notFoundWords))
    return notFoundWords


def find_word(word):
    # searches for word in dictionary file
    word = word.lower() + '\n'
    with open(wordlist, 'r') as dictionary:
        for line in dictionary:
            if word == line:
                    return line
    return -1

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
print(read_tweets())
