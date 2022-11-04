# ==== a utility function for long-term purpose ====

import string, re
import csv
import os

from twarc import Twarc2, expansions
from .constant import *
import datetime
import json


# ==== tweet crawling ====
def tweet_look_up_by_id(tweet_ids: list, client):
    lookup = client.tweet_lookup(tweet_ids=tweet_ids)
    tweet_res = []
    try:
        for page in lookup:
            try:
                result = expansions.flatten(page)
                for tweet in result:
                    tweet_res.append(tweet)
            except ValueError:
                print(f"skip one unaccessible tweet id in one page and continue")
                continue
        if len(tweet_res) < 1:
            return None
        else:
            return tweet_res
    except ValueError:
        print(f"encounter one unaccessible tweet id in one lookup(batch)")
        return None


def whole_convo_crawling(tweets, saved_convo_dir, client):
    # look up the whole conversation from a tweet-id
    for tweet_obj in tweets:
        tweet_id = tweet_obj[ID]

        convo_csv_fp = f"{saved_convo_dir}/{tweet_id}.text"        #%%
        created_at = tweet_obj[CREATED_AT]
        # print(created_at)     #%%
        year = created_at[0:4]
        month = created_at[5:7]
        day = created_at[8:10]       #%%
        conv_id = tweet_obj[CONVERSATION_ID]
        print(f" process tweet-id: {tweet_id}, convo-id: {conv_id}")
        
        if tweet_id != conv_id:
            if_tweet_id_different_convo_id = True
            convo_csv_fp_real = f"{saved_convo_dir}/{conv_id}.text"
        else:
            if_tweet_id_different_convo_id = False

        if os.path.exists(convo_csv_fp):
            print(f'file: {convo_csv_fp} exists, and move to the next one')
            continue

        start_time = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0,
                                    datetime.timezone.utc)        #%%
        query = f"conversation_id:{conv_id}"
        search_results = client.search_all(query=query,
                                        start_time=start_time, max_results=100)
        if_have_convo_data = False
        for page in search_results:
            # put the page loop first, since, we may not have the conversations
            result = expansions.flatten(page)
            for tweet in result:
                # print(tweet[TEXT])
                if_have_convo_data = True
                if if_tweet_id_different_convo_id:
                    with open(convo_csv_fp, 'a+') as f:
                        f.write(json.dumps(tweet) + '\n')
                    with open(convo_csv_fp_real, 'a+') as f:
                        f.write(json.dumps(tweet) + '\n')
                else:
                    with open(convo_csv_fp, 'a+') as f:
                        f.write(json.dumps(tweet) + '\n')     
        if not if_have_convo_data:
            if if_tweet_id_different_convo_id:
                with open(convo_csv_fp, 'a+') as f:
                    f.write('None' + '\n')
                with open(convo_csv_fp_real, 'a+') as f:
                    f.write('None' + '\n')
            else:
                with open(convo_csv_fp, 'a+') as f:
                    f.write('None' + '\n')  


def tweet_1reply_2reply_csv_creation(txt_file, saved_convo_csv_directory, client):
    # example: txt_file = f'{1451660101614555145}.text'

    tweet_id = txt_file.split('/')[-1].split('.')[0]
    
    # step x: invalid tweet id
    with open(txt_file, 'r') as lines:
        for line in lines:
            if line.startswith('None'):
                print(f'unaccessible tweet id of: {tweet_id}')
                return None
            else:
                pass

    # step x: existance of csv of tweet conversation
    csv_fp = f'{saved_convo_csv_directory}/{tweet_id}.csv'
    if os.path.exists(csv_fp):
        print(f'file: {csv_fp} exists, and move to the next one')
        return None

    # step x: file collection and summarization
    tweet_obj = tweet_look_up_by_id([tweet_id], client=client)
    # # file preparation only 
    # whole_convo_crawling(tweet_obj, saved_convo_dir='./', client=Twarc2(bearer_token=BEAR_CDOE_BH))
    # # end 
    tweet_obj = tweet_obj[0]
    print(f'process conversation related to tweet-id: {tweet_obj[ID]}')

    referenced_id2tweet_obj = {}

    with open(txt_file, 'r') as f:
        for line in f:
            tweet_obj_in_convo = json.loads(line)
            referenced_tweet_id = tweet_obj_in_convo[REFERENCED_TWEET][0][ID]
            if referenced_tweet_id in referenced_id2tweet_obj:
                referenced_id2tweet_obj[referenced_tweet_id].append(tweet_obj_in_convo)
            else:
                referenced_id2tweet_obj[referenced_tweet_id] = [tweet_obj_in_convo]
    # write (id, tweet, 1-level reply) csv
    # write (id, tweet, 1-level reply, 2-level reply) csv
    with open(csv_fp, "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        header = ["id", "tweet", "1-level_reply", '2-level_reply']
        csv_writer.writerow(header)
        csv_writer.writerow([tweet_obj[ID], tweet_obj[TEXT], '', ''])
        
        for index, first_level_reply in enumerate(referenced_id2tweet_obj[tweet_obj[ID]]):
            # write 1-level reply
            csv_writer.writerow([first_level_reply[ID], '', first_level_reply[TEXT], ''])
            # write 2-level reply
            if first_level_reply[ID] in referenced_id2tweet_obj:
                for second_level_reply in referenced_id2tweet_obj[first_level_reply[ID]]:
                    csv_writer.writerow([second_level_reply[ID], '', '', second_level_reply[TEXT]])

# ==== text process ====
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