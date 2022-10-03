# ==== a utility function for long-term purpose ====

import string, re
import csv
# by bing
def strip_all_entities(text):
    # ==== error 1 ====: isn't -> isn t
    # entity_prefixes = ['@']
    # for separator in string.punctuation:
    #     if separator not in entity_prefixes:
    #         text = text.replace(separator, ' ')
    # words = []
    # for word in text.split():
    #     word = word.strip()
    #     if word:
    #         if word[0] not in entity_prefixes:
    #             words.append(word)
    # return ' '.join(words)
    user_mention_patter = r"(?:\@|https?\://)\S+"
    tweet_text = re.sub(user_mention_patter, "", text)
    return tweet_text

# it fails on this tweet: call @Susan @My 5g via @full @tre
def remove_leading_usernames(tweet):
    """
        Remove all user handles at the beginning of the tweet.

        Parameters
        -----------------
        tweet : str, a valid string representation of the tweet text
    """
    regex_str = '^[\s.]*@[A-Za-z0-9_]+\s+'

    original = tweet
    change = re.sub(regex_str, '', original)

    while original != change:
        original = change
        change = re.sub(regex_str, '', original)

    return change

def process_tweet(tweet):
    """
        Preprocess tweet. Remove URLs, leading user handles, retweet indicators, emojis,
        and unnecessary white space, and remove the pound sign from hashtags. Return preprocessed
        tweet in lowercase.

        Parameters
        -----------------
        tweet : str, a valid string representation of the tweet text
    """

    #Remove www.* or https?://*
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))\s+','',tweet)
    tweet = re.sub('\s+((www\.[^\s]+)|(https?://[^\s]+))','',tweet)
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))',' ',tweet)
    #Remove RTs
    tweet = re.sub('^RT @[A-Za-z0-9_]+: ', '', tweet)
    # Incorrect apostraphe
    tweet = re.sub(r"’", "'", tweet)
    #Remove @username
    # solution 1 by Caleb:
    # tweet = remove_leading_usernames(tweet)
    # solution 2 by bing with some improvement:
    tweet = strip_all_entities(tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #Replace ampersands
    tweet = re.sub(r' &amp; ', ' and ', tweet)
    tweet = re.sub(r'&amp;', '&', tweet)
    #Remove emojis
    tweet = re.sub(r'[^\x00-\x7F]+', '', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet.lower().strip()