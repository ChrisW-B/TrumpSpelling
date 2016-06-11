import tweepy
import config
import re
import sys
import time
import thread

wordlist = "wordlist.txt"
syllablelist = "syllablelist.txt"
reload(sys)
sys.setdefaultencoding('utf8')  #twitter doesn't get along with ascii


class HaikuListener(tweepy.StreamListener):
    # override tweepy.StreamListener to add logic to on_status
    def on_status(self, status):
        numSyllables = countSyllables(status.text)
        if numSyllables == [5, 7, 5]:
            print("Found haiku!")
            api.create_favorite(status.id)
            api.update_status("@"+ status.author.screen_name + " Nice haiku!", in_reply_to_status_id=status.id)
   
    def on_error(self, status_code):
        print(status_code)


def countSyllables(tweet):
    # creates an array of syllables out of a tweet
    # to be checked for haikus
    stripUrl = re.sub(r"http\S+", "", tweet)
    stripMentions = re.sub(r"@\S+", "", stripUrl)
    stripRTs = stripMentions.replace("RT", "")
    tweetArray = re.findall(r"[\w']+", stripRTs)
    totalSyllables = [0, 0, 0]
    for word in tweetArray:
        ind = findWord(word + '\n')
        wordSyllables = 0
        if ind > -1:
            wordSyllables = getSyllables(ind)
        else:
            wordSyllables = guessSyllables(word)
        if totalSyllables[0] < 5:
            totalSyllables[0] += wordSyllables
        elif totalSyllables[1] < 7:
            totalSyllables[1] += wordSyllables
        else:
            totalSyllables[2] += wordSyllables
    return totalSyllables


def findWord(word):
    # searches for word in dictionary file
    word = word.lower()
    with open(wordlist) as myFile:
        for num, line in enumerate(myFile):
            if word in line:
                if word == line.lower():
                    return num
    return -1


def getSyllables(ind):
    # goes to an index of the syllable file and splits up word to
    # count syllables
    with open(syllablelist) as myFile:
        for num, line in enumerate(myFile):
            if (num == ind):
                syllables = re.findall(r"[\w']+", line)
                return len(syllables)


def guessSyllables(word):
    # borrowed from:
    #  http://stackoverflow.com/questions/14541303/count-the-number-of-syllables-in-a-word
    count = 0
    vowels = 'aeiouy'
    word = word.lower().strip(".:;?!")
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count += 1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count += 1
    if count == 0:
        count += 1
    return count


def limit_handled(cursor):
    # handles twitter limiting and tries to find people
    # who follow
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15*60)


def follow_back():
    #teamfollowback!
    while True:
        for follower in limit_handled(tweepy.Cursor(api.followers).items()):
            # maybe keep out the spammers
            if follower.friends_count/follower.followers_count < 3 or follower.friends_count < 100:
                follower.follow()
                print("following " + follower.screen_name)
        time.sleep(15*60)

#authorize tweepy
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)

#set up stream
haikuListener = HaikuListener()
haikuStream = tweepy.Stream(auth=api.auth, listener=haikuListener)
haikuStream.userstream(async=True)
thread.start_new_thread(follow_back, ())
api.update_status("@ChrisW_B I'm ready!")
