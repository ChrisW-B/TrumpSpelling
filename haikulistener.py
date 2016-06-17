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


class HaikuSampleListener(tweepy.StreamListener):
    # override tweepy.StreamListener to add logic to on_status
    def on_status(self, status):
        numSyllables = count_syllables(status.text)
        if numSyllables == [5, 7, 5]:
            print("Found non follow haiku!")
            api.create_favorite(status.id)

    def on_error(self, status_code):
        print(status_code)


class HaikuUserListener(tweepy.StreamListener):
    def on_status(self, status):
        numSyllables = count_syllables(status.text)
        if numSyllables == [5, 7, 5]:
            print("Found follower haiku!")
            api.create_favorite(status.id)
            api.update_status("@" + status.author.screen_name + " Nice haiku!", in_reply_to_status_id=status.id)

    def on_error(self, status_code):
        print(status_code)


def count_syllables(tweet):
    # creates an array of syllables out of a tweet
    # to be checked for haikus
    stripUrl = re.sub(r"http\S+", "", tweet)
    stripMentions = re.sub(r"@\S+", "", stripUrl)
    stripTags = re.sub(r"#\S+", "", stripMentions)
    stripRTs = stripTags.replace("RT", "")
    tweetArray = re.findall(r"[\w']+", stripRTs)

    totalSyllables = [0, 0, 0]
    for word in tweetArray:
        ind = find_word(word + '\n')
        wordSyllables = 0
        if ind > -1:
            wordSyllables = get_syllables(ind)
        else:
            wordSyllables = guess_syllables(word)
        if totalSyllables[0] < 5:
            totalSyllables[0] += wordSyllables
        elif totalSyllables[1] < 7:
            totalSyllables[1] += wordSyllables
        else:
            totalSyllables[2] += wordSyllables
    return totalSyllables


def find_word(word):
    # searches for word in dictionary file
    word = word.lower()
    with open(wordlist) as myFile:
        for num, line in enumerate(myFile):
            if word in line:
                if word == line.lower():
                    return num
    return -1


def get_syllables(ind):
    # goes to an index of the syllable file and splits up word to
    # count syllables
    with open(syllablelist) as myFile:
        for num, line in enumerate(myFile):
            if (num == ind):
                syllables = re.findall(r"[\w']+", line)
                return len(syllables)


def guess_syllables(word):
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
        print("starting follow")
        for follower in limit_handled(tweepy.Cursor(api.followers).items()):
            # maybe keep out the spammers
            if follower.friends_count/follower.followers_count < 3 or follower.friends_count < 100:
                follower.follow()
                print("following " + follower.screen_name)
        time.sleep(15*60)


def user_listener():
    while True:
        try:
            # For accounts bot is following
            print("starting user")
            haikuUserListener = HaikuUserListener()
            haikuUserStream = tweepy.Stream(auth=api.auth, listener=haikuUserListener)
            haikuUserStream.userstream(async=False)
        except:
            continue


def sample_listener():
    while True:
        try:
            # for sample stream
            print("starting sample")
            haikuSampleListener = HaikuSampleListener()
            haikuSampleStream = tweepy.Stream(auth=api.auth, listener=haikuSampleListener)
            haikuSampleStream.sample(async=False)
        except:
            time.sleep(15*60)
            continue


def setup_threads():
    # set up streams
    thread.start_new_thread(user_listener, ())
    thread.start_new_thread(sample_listener, ())
    # start follow back
    # thread.start_new_thread(follow_back, ())

#authorize tweepy
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
setup_threads()
api.update_status("@ChrisW_B I'm ready!")

while True:
    #Keep the main thread alive
    time.sleep(1)
