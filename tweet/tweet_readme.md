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
# 3.
# references: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/6a-labs-code-academic-python.md
# search function: client.search() for only 30 days by Standard API2. 
# client.search_all() The search_all method call the full-archive search endpoint to get the Tweets (replies) for the conversation
# this only exists on the academic api
# broader introduction: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md#give-me-all-tweets-in-the-conversation-thread-with-conversation_id-1394699198382043136
# explanation of max_results=100: 
# The max_results parameter for the search_all method above tells Twarc how many Tweets to get per request. Twarc will get all the Tweets for the specified time period and query, which can be more than the max_results, because it will make multiple calls in the example above and for each call it will get 100 requests until it gets all Tweets for the time period your specified.
# result checking: 1) even if 503, it is still working to expand tweets, and add it to the conv.txt file. But, from the log.txt, we may need to wait for some time on the time stamp. One question is that: what if the tweet has 10M replies. how to handle it?

# todo:
1. 503 response code: https://twittercommunity.com/t/503-response-code-and-httperror/154924