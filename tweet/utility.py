# ==== a utility function for long-term purpose ====

import string, re
import csv
import os

from twarc import Twarc2, expansions
from .constant import *
import datetime
import json
import pandas as pd


# ==== tweet id existence filtering ====
def find_uncrawled_tweet_id(all_tweet_id, crawled_folder):
    all_tweet_id = [ int(i) for i in all_tweet_id]
    existing_tweet_id = [ int(tweet_id_file.split('.')[0]) for tweet_id_file in os.listdir(crawled_folder)]
    crawled_tweet_id = list(set(all_tweet_id) & set(existing_tweet_id))
    uncrawled_tweet_id = list(set(all_tweet_id) - set(existing_tweet_id))
    print(f'{len(crawled_tweet_id)}/{len(all_tweet_id)} has been crawled, we only crawl {len(uncrawled_tweet_id)} tweets')
    all_tweet_id = uncrawled_tweet_id
    return all_tweet_id


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
    # except:
    # when someone changes the academic api key
    #     # maybe it is 
    #     # log requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: 
    #     print(f"encounter one unaccessible tweet id in one lookup(batch)")
    #     return None


def whole_convo_crawling(tweets, saved_convo_dir, client,
        if_limit_num_of_pages=False, num_of_pages=1000):
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

        # if convo is the same
        if os.path.exists(convo_csv_fp):
            print(f'file: {convo_csv_fp} exists, and move to the next one')
            continue
        # if the convo is different
        if if_tweet_id_different_convo_id and os.path.exists(convo_csv_fp_real):
            print(f'file: {convo_csv_fp_real} differernt convo master exists, and move to the next one')
            continue

        start_time = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 0,
                                    datetime.timezone.utc)        
        query = f"conversation_id:{conv_id}"
        search_results = client.search_all(query=query,
                                        start_time=start_time, max_results=100)
        # TODO: find the place where we have 503 response code
        # updated on Nov 4 2022: some conversations are so long, like this 959888315401957376.text
        # for line numbers by "wc -l xx.text". at least: 903015
        print('after search_all conversation query, start to expand results')
        if_have_convo_data = False
        # for one page: it will contain at most 100 crawled tweets
        # search_results will have multiple calls for N*100 tweets of the thread for the check up
        for page_id, page in enumerate(search_results):
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
            # ==== if we only focus on 100*num_of_pages replies
            if if_limit_num_of_pages:
                if page_id > num_of_pages:
                    print('we stop the conversation search due to the page limit')
                    break                    
            # ==== end ====
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
    # tweet id: sometimes, we cannot crawl the tweet id again, like: 1355286194058387463, found on Nov 3 2022
    # Based on this, I add the following check
    if tweet_obj == None:
        return None
    if tweet_obj is None:
        return None

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
        header = ['id', 'referenced_id', 'tweet', '1_level_reply', '2_level_reply']
        csv_writer.writerow(header)
        csv_writer.writerow([tweet_obj[ID], '', tweet_obj[TEXT], '', ''])
        
        # error on tweet id: 1374790691998593026
        # add the following if line
        if tweet_obj[ID] in referenced_id2tweet_obj:
            for _, first_level_reply in enumerate(referenced_id2tweet_obj[tweet_obj[ID]]):
                # write 1-level reply
                csv_writer.writerow([first_level_reply[ID], tweet_obj[ID], '', first_level_reply[TEXT], ''])
                # write 2-level reply
                if first_level_reply[ID] in referenced_id2tweet_obj:
                    for second_level_reply in referenced_id2tweet_obj[first_level_reply[ID]]:
                        csv_writer.writerow([second_level_reply[ID], first_level_reply[ID], '', '', second_level_reply[TEXT]])

def expand_tweet_and_1level_reply(tweet_convo_in_csv):
    tweet_convo_in_df = pd.read_csv(tweet_convo_in_csv, dtype=str)
    df = tweet_convo_in_df
    FIRST_LEVEL_REPLY = '1_level_reply'
    TWEET = 'tweet'

    if df[df[FIRST_LEVEL_REPLY].notnull()].shape[0] > 0:
        # make the tweet, 1-level reply row in the dataframe
        df_merged = pd.merge(df[df[FIRST_LEVEL_REPLY].notnull()].drop(['tweet', '2_level_reply'], axis=1), 
                            df[df[TWEET].notnull()][['id', 'tweet']], left_on='referenced_id', right_on='id')
        df_merged = df_merged.rename(columns={'id_x': 'id'}) # or inplace=True
        df_merged = df_merged.drop(['id_y'], axis=1)
        df_merged = df_merged[['id', 'referenced_id', 'tweet', '1_level_reply']]

        # add the # of 2-level replies
        group_data_stat = df.groupby(['referenced_id']).size()
        group_data_stat = group_data_stat.reset_index()
        group_data_stat.columns = ['referenced_id', '#_of_2level_replies']
        # group_data_stat
        df_merged = pd.merge(df_merged, group_data_stat, left_on='id', right_on='referenced_id', how='left')\
            .drop(['referenced_id_y'], axis=1)\
            .rename(columns={'referenced_id_x': 'referenced_id'})

        return df_merged
    else:
        return None

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
    tweet = re.sub(r"???", "'", tweet)
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