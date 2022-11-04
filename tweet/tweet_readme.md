# 1.
# when crawling the tweet conversation
# if use the batch size of 1000 for one key, then, we can easily get sleeping, it will traverse the whole 1000 and passes
# the limit. Instead, when i use the batch size of 100 for one key, we can quickly iterate and move fast.
# from the rate limit: sleeping time changes from 900 seconds to 110 seconds!
# references: 1) chunk size of 100: https://github.com/EnyanDai/FakeHealth/blob/master/API/collect_tweets.py
# understand the API setup better. 
# 2.
# twitter response code: https://developer.twitter.com/ja/docs/basics/response-codes
# 2.1 code 503: caught 503 from Twitter API, sleeping 1

# todo:
1. 503 response code: https://twittercommunity.com/t/503-response-code-and-httperror/154924