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
# 3. search and search_all
# references: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/6a-labs-code-academic-python.md
# search function: client.search() for only 30 days by Standard API2. 
# client.search_all() The search_all method call the full-archive search endpoint to get the Tweets (replies) for the conversation
# this only exists on the academic api
# broader introduction: https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md#give-me-all-tweets-in-the-conversation-thread-with-conversation_id-1394699198382043136
# explanation of max_results=100: 
# The max_results parameter for the search_all method above tells Twarc how many Tweets to get per request. Twarc will get all the Tweets for the specified time period and query, which can be more than the max_results, because it will make multiple calls in the example above and for each call it will get 100 requests until it gets all Tweets for the time period your specified.
# result checking: 1) even if 503, it is still working to expand tweets, and add it to the conv.txt file. But, from the log.txt, we may need to wait for some time on the time stamp. One question is that: what if the tweet has 10M replies. how to handle it?
# 3.2 standard search_all limit: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all: from the document, it is 300 requests per 15-minute window
# 3.2.1 from my test: at least: 50 request/15 minutes; 3.2.2 but, in the later time, I set it the list to [:2] some time sleeping error can happen, then adjust it to the current 1 element only
# 3.3 result analysis: 1) we have tweet, but no replies; 2) 
# 4. user network crawling
# references: 1) https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list; Reasons: this is list 2) https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-followers
# limit: one request can only get the latest 200 followers/followees. TOCHECK: one page per request or multiple pages per request.
# but, 5000 limit by this: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids . Reason: this is ids. 
# TODO: check twarc to see how this package retrieves the ids for the full list of followers.
# 5. retweet of one tweet
# from PSU: the limit is 200
# TODO: do we have referenced id of a tweet such that we know the original tweet



# todo:
1. 503 response code: https://twittercommunity.com/t/503-response-code-and-httperror/154924