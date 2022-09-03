import datetime
import os

import eli5
import emoji
import joblib
import numpy
import re
import stopwords
import time
import tweepy
import pandas as pd

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from emot.emo_unicode import UNICODE_EMOJI
from googleapiclient.discovery import build
from googletrans import Translator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier

from sentiment.forms import *
from sentiment.models import *


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


def login_function(request):
    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            user = EmailBackend.authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('dashboard'))
                else:
                    messages.warning(request, 'Required user was not verified')
    context = {
        "login_form": login_form
    }
    return render(request, 'signin.html', context)


def sign_up(request):
    register_form = BasicRegForm()
    if request.method == "POST":
        register_form = BasicRegForm(request.POST)
        if register_form.is_valid():
            tec = register_form.save(commit=False)
            password = tec.password
            tec.set_password(password)
            tec.save()
            messages.info(request, 'User register successfully')
            return HttpResponseRedirect(reverse('dashboard'))
    context = {
        "register_form": register_form
    }
    return render(request, 'signup.html', context)


def index(request):
    context = {
        'page_type': "logout"
    }
    return render(request, 'index.html', context)


@login_required
def dashboard(request):
    context = {
        'page_type': "login"
    }
    return render(request, 'dashboard.html', context)


@login_required
def list_youtube_post(request):
    context = {
        "youtube_posts": PostLink.objects.filter(post_type="youtube"),
        'page_type': "login"
    }
    return render(request, 'youtube-list.html', context)


@login_required
def add_youtube_link(request):
    input_form = InputTextForm()
    if request.method == "POST":
        input_form = InputTextForm(request.POST)
        if input_form.is_valid():
            user_form = input_form.save(commit=False)
            user_form.post_type = "youtube"
            user_form.save()
            messages.info(request, 'Add new youtube link successfully')
            return HttpResponseRedirect(reverse('list-youtube-link'))
        else:
            context = {
                'page_type': "login",
                'input_form': input_form,
                "result": False
            }
            return render(request, 'add-youtube.html', context)
    context = {
        'page_type': "login",
        'input_form': input_form,
        "result": False
    }
    return render(request, "add-youtube.html", context)


@login_required
def youtube_update(request, id):
    youtube_post = PostLink.objects.get(id=id)
    youtube_video_id = fetch_youtube_video_id(youtube_post.post_url)
    if youtube_video_id:
        fetch_comments_youtube(youtube_video_id, youtube_post.last_updated, youtube_post)
        messages.info(request, 'Youtube comments fetched successfully')
    else:
        messages.info(request, 'Youtube video id not valid')
    # youtube_post.last_updated = datetime.datetime.now().date().strftime('%Y-%m-%d')
    # youtube_post.save()
    return HttpResponseRedirect(reverse('list-youtube-link'))


@login_required
def youtube_result(request, id):
    overall_analysis = {}
    language_group = {}
    emoji_list = []
    comment_list = []
    translated_emoji = []

    for comments in PostComment.objects.filter(post_id=id):
        comment_list.append(comments.comments)

    # if len(comment_list) > settings.COMMENTS_SIZE:
    if comment_list:
        for comment in comment_list:
            clean_emoji = extract_emojis(comment)
            if clean_emoji:
                emoji_list.append(clean_emoji)
        remove_emoji_from_text = [comment for comment in comment_list if comment not in emoji_list]
        language_group = language_cluster(remove_emoji_from_text)
        for emojis in emoji_list:
            translated_emoji.append(convert_emojis(emojis).replace("_", " "))
        overall_analysis = overall_sentiment_analysis(translated_emoji, language_group, len(comment_list))
        # roman_sentiemnt(comments)
        context = {
            # 'overall_comments': comment_list,
            'emoji_comment': emoji_list,
            'urdu_comment': language_group['urdu_cluster'],
            'english_comment': language_group['english_cluster'],
            'roman_urdu_comment': language_group['roman_cluster'],

            'overall_analysis': [d for d in overall_analysis.values()],
            'overall_language_name': ["Emoji", "urdu", "English", "Roman Urdu"],
            'overall_language_summary': [len(emoji_list), len(language_group['urdu_cluster']),
                                         len(language_group['english_cluster']), len(language_group['roman_cluster'])],
            'english_analysis': language_sentiment_text(language_group['english_cluster']) if language_group[
                'english_cluster'] else {},
            'urdu_analysis': language_sentiment_text(urdu_conversion(language_group['urdu_cluster'])) if language_group[
                'urdu_cluster'] else {},
            # 'roman_urdu_analysis': language_sentiment_text(urdu_conversion(language_group['roman_cluster'])),
            'emoji_analysis': language_sentiment_text(translated_emoji) if translated_emoji else {},
            'features_extraction_': features_extraction_(language_group['english_cluster'])
        }
        return render(request, 'demochart.html', context)
    else:
        messages.info(request, 'Youtube comments are not enough for analysis')


@login_required
def list_twitter_post(request):
    context = {
        "twitter_posts": PostLink.objects.filter(post_type="twitter"),
        'page_type': "login"
    }
    return render(request, 'twitter-list.html', context)


@login_required
def add_twitter_link(request):
    input_form = InputTwitterForm()
    if request.method == "POST":
        input_form = InputTwitterForm(request.POST)
        if input_form.is_valid():
            # TODO: Get youtube details
            # print(input_form.cleaned_data.get('post_url'))
            user_form = input_form.save(commit=False)
            user_form.post_type = "twitter"
            user_form.save()
            messages.info(request, 'Add new twitter link successfully')
            return HttpResponseRedirect(reverse('list-twitter-link'))
        else:
            context = {
                'page_type': "login",
                'input_form': input_form,
                "result": False
            }
            return render(request, 'add-twitter.html', context)
    context = {
        'page_type': "login",
        'input_form': input_form,
        "result": False
    }
    return render(request, "add-twitter.html", context)


@login_required()
def twitter_update(request, id):
    twitter_post = PostLink.objects.get(id=id)
    twitter_name_id = fetch_twitter_name_id(twitter_post.post_url)
    if twitter_name_id:
        fetch_replies_twitter(twitter_name_id['name'], twitter_name_id['twitter_id'], twitter_post)
        messages.info(request, 'Twitter comments fetched successfully')
    else:
        messages.info(request, 'Twitter video id not valid')
    return HttpResponseRedirect(reverse('list-twitter-link'))


@login_required()
def twitter_result(request, id):
    overall_analysis = {}
    language_group = {}
    emoji_list = []
    comment_list = []
    translated_emoji = []

    for comments in PostComment.objects.filter(post_id=id)[:50]:
        comment_list.append(comments.comments.replace("RT: ", ""))

    # if len(comment_list) > settings.COMMENTS_SIZE:
    if comment_list:
        for comment in comment_list:
            clean_emoji = extract_emojis(comment)
            if clean_emoji:
                emoji_list.append(clean_emoji)
        remove_emoji_from_text = [comment for comment in comment_list if comment not in emoji_list]
        language_group = language_cluster(remove_emoji_from_text)
        for emojis in emoji_list:
            translated_emoji.append(convert_emojis(emojis).replace("_", " "))
        overall_analysis = overall_sentiment_analysis(translated_emoji, language_group, len(comment_list))
        # roman_sentiemnt(comments)
        context = {
            # 'overall_comments': comment_list,
            'emoji_comment': emoji_list,
            'urdu_comment': language_group['urdu_cluster'],
            'english_comment': language_group['english_cluster'],
            'roman_urdu_comment': language_group['roman_cluster'],

            'overall_analysis': [d for d in overall_analysis.values()],
            'overall_language_name': ["Emoji", "urdu", "English", "Roman Urdu"],
            'overall_language_summary': [len(emoji_list), len(language_group['urdu_cluster']),
                                         len(language_group['english_cluster']), len(language_group['roman_cluster'])],
            'english_analysis': language_sentiment_text(language_group['english_cluster']) if language_group[
                'english_cluster'] else {},
            'urdu_analysis': language_sentiment_text(urdu_conversion(language_group['urdu_cluster'])) if language_group[
                'urdu_cluster'] else {},
            # 'roman_urdu_analysis': language_sentiment_text(urdu_conversion(language_group['roman_cluster'])),
            'emoji_analysis': language_sentiment_text(translated_emoji) if translated_emoji else {},
            'features_extraction_': features_extraction_(language_group['english_cluster'])
        }
        return render(request, 'demochartTwitter.html', context)
    else:
        messages.info(request, 'Twitter comments are not enough for analysis')


def fetch_twitter_name_id(twitter_url: str) -> dict:
    return {
        "name": twitter_url.split(".com/")[1].split("/status")[0],
        "twitter_id": twitter_url.split("status/")[1].split("?")[0]
    }


def fetch_youtube_video_id(youtube_url: str):
    try:
        return youtube_url.split("watch?v=")[1].split("&ab_channel")[0]
    except Exception as e:
        return None


def clean_tweets(tweet):
    tweet = re.sub("@[A-Za-z0-9_]+", "", tweet)
    tweet = re.sub("#[A-Za-z0-9_]+", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = re.sub(r'www.\S+', '', tweet)
    # remove numbers
    tweet = re.sub(r'\w*\d+\w*', '', tweet)
    # replace over space
    tweet = re.sub('\s{2,}', " ", tweet)

    tweet = tweet.split()
    temp = " ".join(word for word in tweet)
    return temp


def fetch_replies_twitter(twitter_name: str, twitter_tweet: str, post_details):
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    replies = []
    tweets = tweepy.Cursor(
        api.search_tweets,
        q='{}'.format(twitter_name),
        since_id=twitter_tweet,
        result_type='recent'
    ).items()
    try:
        for tweet in tweets:
            replies.append(tweet.text)
            clean_tw = clean_tweets(tweet.text)
            if clean_tw:
                print(f"clean_tw: {clean_tw}")
                PostComment(post=post_details, comments=clean_tw).save()
    except tweepy.TweepyException:
        print("Something went wrong please wait for 15 minutes")


def fetch_comments_youtube(youtube_video_id: str, last_comment_update: datetime.date, post_details: PostLink):
    try:
        video_comments = []
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        video_response = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=youtube_video_id
        ).execute()

        for item in video_response['items']:
            if not last_comment_update:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                last_update = datetime.datetime.strptime(item['snippet']['topLevelComment']['snippet']['updatedAt'][:10], "%Y-%m-%d").strftime("%Y-%m-%d")
                comment = re.sub('[^a-zA-Z0-9 \n\.]', '', comment)
                if comment:
                    print(f"Comment: {comment}")
                    PostComment(post=post_details, comments=comment, last_updated=last_update).save()
            #
            # else:
            #     if item['snippet']['topLevelComment']['snippet']['updatedAt'] < last_comment_update:

    except Exception as e:
        print(f"Something went wrong: {e}")


def extract_emojis(text: str) -> str:
    characters: list
    emoji_list: list
    # # clean_text: str
    # remove all tagging and links, not need for sentiments
    # remove_keys = ("@", "https://", "&", "#")
    # # TODO: It's not necessary
    # clean_text = " ".join(txt for txt in text if not txt.startswith(remove_keys))

    # setup the input, get the characters and the emoji lists
    characters = [chr for chr in text]
    emoji_list = [c for c in characters if c in emoji.UNICODE_EMOJI["en"]]
    clean_emoji = " ".join([chr for chr in text if any(i in chr for i in emoji_list)])
    return clean_emoji


def convert_emojis(text: str) -> str:
    for emojis in UNICODE_EMOJI:
        text = text.replace(emojis, "_".join(UNICODE_EMOJI[emojis].replace(",", "").replace(":", "").split()))
    return text


def language_cluster(sentences: list) -> dict:
    translator = Translator()
    totranslate = translator.translate(sentences)
    english_cluster, urdu_cluster, roman_cluster = [], [], []
    for detection in totranslate:
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        detection.origin = emoji_pattern.sub(r'', detection.origin)
        if detection.src == 'ur':
            urdu_cluster.append(detection.origin)
        elif detection.src == 'en':
            english_cluster.append(detection.origin)
        else:
            roman_cluster.append(detection.origin)
    return {
        "urdu_cluster": urdu_cluster,
        "english_cluster": english_cluster,
        "roman_cluster": roman_cluster
    }


def urdu_conversion(sentence: list):
    translator = Translator()
    converted = translator.translate(sentence)
    text = []
    for translation in converted:
        text.append(translation.text)
    return text


def sentiment_analysis(sentences: list) -> dict:
    if sentences:
        negative_sentiment, positive_sentiment, neutral_sentiment = 0, 0, 0
        for sentence in sentences:
            score = SentimentIntensityAnalyzer().polarity_scores(sentence)
            negative_sentiment += score['neg']
            neutral_sentiment += score['neu']
            positive_sentiment += score['pos']
        return {
            "negative_sentiment": (negative_sentiment / len(sentences)) * 100,
            "neutral_sentiment": (neutral_sentiment / len(sentences)) * 100,
            "positive_sentiment": (positive_sentiment / len(sentences)) * 100
        }


def overall_sentiment_analysis(emoji_analysis: list, languages_clusters: dict, all_comments_len: int) -> dict:
    negative_sentiment, positive_sentiment, neutral_sentiment = 0, 0, 0
    for sentence in emoji_analysis:
        score = SentimentIntensityAnalyzer().polarity_scores(sentence)
        negative_sentiment += score['neg']
        neutral_sentiment += score['neu']
        positive_sentiment += score['pos']

    for urdu_cluster in urdu_conversion(languages_clusters["urdu_cluster"]):
        score = SentimentIntensityAnalyzer().polarity_scores(urdu_cluster)
        negative_sentiment += score['neg']
        neutral_sentiment += score['neu']
        positive_sentiment += score['pos']

    for english_sentence in languages_clusters["english_cluster"]:
        score = SentimentIntensityAnalyzer().polarity_scores(english_sentence)
        negative_sentiment += score['neg']
        neutral_sentiment += score['neu']
        positive_sentiment += score['pos']

    return {
        "neutral_sentiment": (neutral_sentiment / all_comments_len) * 100,
        "negative_sentiment": (negative_sentiment / all_comments_len) * 100,
        "positive_sentiment": (positive_sentiment / all_comments_len) * 100
    }


def language_sentiment_text(comments: list) -> dict:
    negative_sentiment, positive_sentiment, neutral_sentiment = [], [], []
    for sentence in comments:
        score = SentimentIntensityAnalyzer().polarity_scores(sentence)
        negative_ = score['neg']
        neutral_ = score['neu']
        positive_ = score['pos']
        if positive_ == negative_:
            neutral_sentiment.append(sentence)
        elif positive_ > negative_:
            positive_sentiment.append(sentence)
        else:
            negative_sentiment.append(sentence)

    return {
        "negative_sent": negative_sentiment,
        "neutral_sent": neutral_sentiment,
        "positive_sent": positive_sentiment
    }


def features_extraction_(comments: list) -> list:
    final_vocab = []
    vocab = tokenize(comments)
    for sentence in comments:
        words = word_extraction(sentence)
        bag_vector = numpy.zeros(len(vocab))
        for w in words:
            for i, word in enumerate(vocab):
                if word == w:
                    # bag_vector[i] += 1
                    # print("{0}\n{1}\n".format(sentence, numpy.array(bag_vector)))
                    final_vocab.append(w)
    return final_vocab


def word_extraction(sentence: list) -> list:
    ignore = stopwords.get_stopwords('english')
    words = re.sub("[^\w]", " ", sentence).split()
    return [w.lower() for w in words if w not in ignore]


def tokenize(sentences: list) -> list:
    words = []
    for sentence in sentences:
        w = word_extraction(sentence)
        words.extend(w)
        words = sorted(list(set(words)))
    return words


def roman_sentiemnt(comments: list) -> dict:
    workpath = os.path.dirname(os.path.abspath(__file__))
    c = open(os.path.join(workpath, 'Roman Urdu DataSet.csv'), 'rb')
    data = pd.read_csv(c)

    numpy_array = data.values
    X = numpy_array[:, 0]
    # Clean X here
    X_train = array_cleaner(X)
    y_train = numpy_array[:, 1]
    ngram = 3
    vectorizer = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, ngram), max_df=0.5)
    # X_train = vectorizer.fit_transform(X_train)
    clf = SGDClassifier(alpha=.0001, penalty="elasticnet")
    clf.fit(X_train, y_train)
    eli5.show_prediction(clf, doc="yeh goan bht ganda ha")

    print("working")

    return {}


def cleaner(word):
    word = re.sub(r'\#\.', '', word)
    word = re.sub(r'\n', '', word)
    word = re.sub(r',', '', word)
    word = re.sub(r'\-', ' ', word)
    word = re.sub(r'\.', '', word)
    word = re.sub(r'\\', ' ', word)
    word = re.sub(r'\\x\.+', '', word)
    word = re.sub(r'\d', '', word)
    word = re.sub(r'^_.', '', word)
    word = re.sub(r'_', ' ', word)
    word = re.sub(r'^ ', '', word)
    word = re.sub(r' $', '', word)
    word = re.sub(r'\?', '', word)
    return word.lower()


def hashing(word):
    word = re.sub(r'ain$', r'ein', word)
    word = re.sub(r'ai', r'ae', word)
    word = re.sub(r'ay$', r'e', word)
    word = re.sub(r'ey$', r'e', word)
    word = re.sub(r'ie$', r'y', word)
    word = re.sub(r'^es', r'is', word)
    word = re.sub(r'a+', r'a', word)
    word = re.sub(r'j+', r'j', word)
    word = re.sub(r'd+', r'd', word)
    word = re.sub(r'u', r'o', word)
    word = re.sub(r'o+', r'o', word)
    word = re.sub(r'ee+', r'i', word)
    if not re.match(r'ar', word):
        word = re.sub(r'ar', r'r', word)
    word = re.sub(r'iy+', r'i', word)
    word = re.sub(r'ih+', r'eh', word)
    word = re.sub(r's+', r's', word)
    if re.search(r'[rst]y', 'word') and word[-1] != 'y':
        word = re.sub(r'y', r'i', word)
    if re.search(r'[bcdefghijklmnopqrtuvwxyz]i', word):
        word = re.sub(r'i$', r'y', word)
    if re.search(r'[acefghijlmnoqrstuvwxyz]h', word):
        word = re.sub(r'h', '', word)
    word = re.sub(r'k', r'q', word)
    return word


def array_cleaner(array):
    # X = array
    X = []
    for sentence in array:
        clean_sentence = ''
        words = str(sentence).split(' ')
        for word in words:
            clean_sentence = clean_sentence + ' ' + cleaner(word)
            X.append(clean_sentence)
    return X

