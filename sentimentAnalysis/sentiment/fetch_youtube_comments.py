# import re
#
# from django.conf import settings
# from googleapiclient.discovery import build
#
# youtube_video_id = "rV_3Lewxx6o"
# YOUTUBE_API_KEY = "AIzaSyBTPGddJsNUFeOMuiErEbo_JDsW7Y65ArM"
#
# video_comments = []
# youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
# video_response = youtube.commentThreads().list(
#     part='snippet,replies',
#     videoId=youtube_video_id
# ).execute()
#
# for item in video_response['items']:
#     comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
#     comment = re.sub('[^a-zA-Z0-9 \n\.]', '', comment)
#     video_comments.append(comment)
#
# print(video_comments)



import csv
import tweepy
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# Oauth keys
consumer_key = 'Kmdm3BgHt7Qt5lFkiIJgVw402'
consumer_secret = 'tWzooq0YbtxJXrJAcqrIJVTzXdo10TZzb5TwWutxv5PNXtEaKj'
access_token = '943100209785077760-TOx2RSACitTVddMj99lLW6vwSr3Y9BX'
access_token_secret = 'jEKHx8sbl4T5Jy6eJrDYxVz57Fj8vjDYt5xKas0JOR8nF'
# Authentication with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
# update these for the tweet you want to process replies to 'name' =
# the account username and you can find the tweet id within the tweet URL
name = '@EricssonCareers'
tweet_id = '1514676894666477572'
# name = '@LunarCRUSH'
# tweet_id = '1270923526690664448'
replies = []
print("Starting")
# q="@username", since_id=tweet_id
for tweet in tweepy.Cursor(api.search_tweets, q='{}'.format(name), since_id=tweet_id, result_type='recent').items():
    # if hasattr(tweet, 'in_reply_to_status_id_str'):
        # if tweet.in_reply_to_status_id_str == tweet_id:
        replies.append(tweet.text)

print(replies)