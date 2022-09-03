import re

import tweepy
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from percentage import percentage
from textblob import TextBlob
# from langdetect import detect
import emoji
from emot.emo_unicode import UNICODE_EMOJI
from googleapiclient.discovery import build
from googletrans import Translator
# import indicnlp.transliterate.unicode_transliterate
# from indicnlp.transliterate.unicode_transliterate.ItransTransliterator import ItransTransliterator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.conf import settings

# Create your views here.
from sentiment.forms import InputTextForm, BasicRegForm, LoginForm


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
    return render(request, 'index.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard123.html')


@login_required
def youtube_result(request):
    input_form = InputTextForm()
    if request.method == "POST":
        input_form = InputTextForm(request.POST)
        overall_analysis = {}
        language_group = {}
        emoji_list = []
        comment_list = []
        translated_emoji = []
        if input_form.is_valid():
            # TODO: Get youtube details
            print(input_form.cleaned_data.get('input_url'))
            youtube_video_id = fetch_youtube_video_id(input_form.cleaned_data.get('input_url'))
            # print(input_form.cleaned_data('input_url'))
            if youtube_video_id:
                comment_list = fetch_comments_youtube(youtube_video_id)
                # comment_list = ["میں معافی چاہتا ہوں", "میں ٹھیک ہوں", "I am fine", "Video achi hai", "My name is khan 😂", "☮ 🙂 ❤"]
                # if len(comment_list) > settings.COMMENTS_SIZE:

                for comment in comment_list:
                    clean_emoji = extract_emojis(comment)
                    if clean_emoji:
                        emoji_list.append(clean_emoji)
                # Remove emojis from text
                remove_emoji_from_text = [comment for comment in comment_list if comment not in emoji_list]
                language_group = language_cluster(remove_emoji_from_text)
                for emojis in emoji_list:
                    translated_emoji.append(convert_emojis(emojis).replace("_", " "))
                overall_analysis = overall_sentiment_analysis(translated_emoji, language_group, len(comment_list))
        context = {
            'input_form': input_form,
            'result': True,
            'overall_comments': comment_list,
            'overall_analysis': overall_analysis,
            'overall_language_name': ["Emoji", "urdu", "English", "Roman Urdu"],
            'overall_language_summary': [len(emoji_list), len(language_group['urdu_cluster']),
                                         len(language_group['english_cluster']), len(language_group['roman_cluster'])],
            'english_comment': language_group['english_cluster'],
            'english_analysis': sentiment_analysis(language_group['english_cluster']),
            'urdu_comment': language_group['urdu_cluster'],
            'urdu_analysis': sentiment_analysis(urdu_conversion(language_group['urdu_cluster'])),
            'emoji_comment': emoji_list,
            'emoji_analysis': sentiment_analysis(translated_emoji),
        }
        print(context)
        return render(request, 'demochart.html', context)
    context = {
        'input_form': input_form,
        "result": False
    }
    return render(request, 'youtube-result.html', context)


@login_required()
def twitter_result(request):
    input_form = InputTextForm()
    if request.method == "POST":
        input_form = InputTextForm(request.POST)
        overall_analysis = {}
        language_group = {}
        emoji_list = []
        comment_list = []
        translated_emoji = []
        if input_form.is_valid():
            # TODO: Get twitter details
            print(input_form.cleaned_data.get('input_url'))
            twitter_name_id = fetch_twitter_name_id(input_form.cleaned_data.get('input_url'))
            # print(input_form.cleaned_data('input_url'))
            if twitter_name_id:
                comment_list = fetch_replies_twitter(twitter_name_id['name'],twitter_name_id['twitter_id'])
                # comment_list = ["میں معافی چاہتا ہوں", "میں ٹھیک ہوں", "I am fine", "Video achi hai", "My name is khan 😂", "☮ 🙂 ❤"]
                # if len(comment_list) > settings.COMMENTS_SIZE:

                for comment in comment_list:
                    clean_emoji = extract_emojis(comment)
                    if clean_emoji:
                        emoji_list.append(clean_emoji)
                # Remove emojis from text
                remove_emoji_from_text = [comment for comment in comment_list if comment not in emoji_list]
                language_group = language_cluster(remove_emoji_from_text)
                for emojis in emoji_list:
                    translated_emoji.append(convert_emojis(emojis).replace("_", " "))
                overall_analysis = overall_sentiment_analysis(translated_emoji, language_group, len(comment_list))
        context = {
            'input_form': input_form,
            'result': True,
            'overall_comments': comment_list,
            'overall_analysis': overall_analysis,
            'overall_language_name': ["Emoji", "urdu", "English", "Roman Urdu"],
            'overall_language_summary': [len(emoji_list), len(language_group['urdu_cluster']),
                                         len(language_group['english_cluster']), len(language_group['roman_cluster'])],
            'english_comment': language_group['english_cluster'],
            'english_analysis': sentiment_analysis(language_group['english_cluster']),
            'urdu_comment': language_group['urdu_cluster'],
            'urdu_analysis': sentiment_analysis(urdu_conversion(language_group['urdu_cluster'])),
            'emoji_comment': emoji_list,
            'emoji_analysis': sentiment_analysis(translated_emoji),
        }
        print(context)
        return render(request, 'twitter-result.html', context)
    context = {
        'input_form': input_form,
        "result": False
    }
    return render(request, 'twitter-result.html', context)

def fetch_twitter_name_id(twitter_url: str) -> dict:
    return {
        "name": twitter_url.split(".com/")[1].split("/status")[0],
        "twitter_id": twitter_url.split("status/")[1].split("?")[0]
    }


def fetch_youtube_video_id(youtube_url: str) -> str:
    return youtube_url.split("watch?v=")[1].split("&ab_channel")[0]


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


def fetch_replies_twitter(twitter_name: str, twitter_tweet: str) -> list:
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    replies = []
    # q="@username", since_id=tweet_id
    for tweet in tweepy.Cursor(api.search_tweets, q='{}'.format(twitter_name), since_id=twitter_tweet,
                               result_type='recent').items():
        replies.append(tweet.text)
    return [clean_tweets(tw) for tw in replies]


def fetch_comments_youtube(youtube_video_id: str) -> list:
    video_comments = []
    youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
    video_response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=youtube_video_id
    ).execute()

    for item in video_response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comment = re.sub('[^a-zA-Z0-9 \n\.]', '', comment)
        video_comments.append(comment)
    return video_comments


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
    print(len(sentences))
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
        "negative_sentiment": (negative_sentiment / all_comments_len) * 100,
        "neutral_sentiment": (neutral_sentiment / all_comments_len) * 100,
        "positive_sentiment": (positive_sentiment / all_comments_len) * 100
    }
# def emp(request):
#     if request.method == "POST":
#         form = PostUrlForm(request.POST)
#         if form.is_valid():
#             try:
#                 form.save()
#                 return redirect('/show')
#             except:
#                 pass
#     else:
#         form = PostUrlForm()
#     return render(request, 'crud.html', {'form': form})
#
#
# def show(request):
#     employees = PostUrl.objects.all()
#     return render(request, "crud.html", {'employees': employees})
#
#
# def edit(request, id):
#     employee = PostUrl.objects.get(id=id)
#     return render(request, 'edit.html', {'employee': employee})
#
#
# def update(request, id):
#     employee = PostUrl.objects.get(id=id)
#     form = PostUrlForm(request.POST, instance=employee)
#     if form.is_valid():
#         form.save()
#         return redirect("/show")
#     return render(request, 'edit.html', {'employee': employee})
#
#
# def destroy(request, id):
#     employee = PostUrl.objects.get(id=id)
#     employee.delete()
#     return redirect("/show")
#
