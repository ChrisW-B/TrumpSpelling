#Twitter Haiku Bot

Just a simple Tweepy based bot that looks for haikus that people it follows tweet

Make sure to install Tweepy before running!

```python
pip install tweepy
```

After that, its as simple as setting up a config.py file like so
```python
consumer_key = "XXXXXXXX"
consumer_secret = "XXXXXXXX"
access_token = "XXXXXXXX-XXXXXXXX"
access_token_secret = "XXXXXXXX"
```

and then running `python haikulistener.py`

Syllable information comes from
http://www.gutenberg.org/ebooks/3204

Syllable guessing comes from 
http://stackoverflow.com/questions/14541303/count-the-number-of-syllables-in-a-word