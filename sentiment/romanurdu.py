from percentage import percentage
from textblob import TextBlob
# from langdetect import detect
import emoji
from googletrans import Translator
# import indicnlp.transliterate.unicode_transliterate
# from indicnlp.transliterate.unicode_transliterate.ItransTransliterator import ItransTransliterator
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# after detect language store corresponding text in these lists
urdu = []
eng = []
roman = []

# def sentiment_analysis(sentence):
#     for sen in sentence:
#         analysis=TextBlob(sen)
#         score = SentimentIntensityAnalyzer().polarity_scores(sen)
#     # print(score)
#         neg = score['neg']
#         neu = score['neu']
#         pos = score['pos']
#     if neg > pos:
#         return "Negative"
#     elif pos > neg:
#         return "Positive"
#     elif pos == neg:
#         return "Neutral"
#
#     noOfTweets=50
#     # changed value from positive to pos and vice versa
#     positive=percentage(pos,noOfTweets)
#     negative=percentage(neg,noOfTweets)
#     neutral=percentage(neu,noOfTweets)
#     positive=format(positive,'.1f')
#     negative=format(negative,'.1f')
#     neutral=format(neutral,'.1f')
#
# global positive
# positive = 60
# global negative
# negative = 0
# global neutral
# neutral = 0
#
#
#
# # translate language
# def urduconversion(sentence):
#     translator = Translator()
#     # text = ["میں معافی چاہتا ہوں", "میں ٹھیک ہوں"]
#     converted = translator.translate(sentence)
#     text = []
#     for translation in converted:
#         # print(translation.text)
#         text.append(translation.text)
#     return text
#
#
# text1 = ["میں معافی چاہتا ہوں", "میں ٹھیک ہوں","I am fine","Video achi hai","😂"]
# def extraction(text = text1):
#     global characters, emoji_list
#     # remove all tagging and links, not need for sentiments
#     remove_keys = ("@", "http://", "&", "#")
#     clean_text = " ".join(
#         txt for txt in text.split()
#             if not txt.startswith(remove_keys)
#     )
#     #     print(clean_text)
#
#     # setup the input, get the characters and the emoji lists
#     characters = [chr for chr in text]
#     emoji_list = [c for c in characters if c in emoji.UNICODE_EMOJI["en"]]  # <-- HERE!
#
#     # extract text
#     clean_text = " ".join(
#         [
#             chr
#             for chr in clean_text.split()
#             if not any(i in chr for i in emoji_list)
#         ]
#     )
#
#     # extract emoji
#     clean_emoji = " ".join(
#         [chr for chr in text.split() if any(i in chr for i in emoji_list)]
#     )
#     return clean_text, clean_emoji
#
#
# characters, emoji_list = 0, 0
# (clean_text, clean_emoji) = extraction()
# print("\nAll Char:", characters)
# print("\nAll Emoji:", emoji_list)
# print("\n", clean_text)
# print("\n", clean_emoji)
#
#

# detect language
def detectlan(sentence):
    translator = Translator()
    totranslate = translator.translate(sentence)
    sourcelang = []
    for detection in totranslate:
        sourcelang.append(detection.src)
        # return urdu
        if detection.src == 'ur':
            urdu.append(detection.origin)
        # return eng
        elif detection.src == 'en':
            eng.append(detection.origin)
        else:
            roman.append(detection.origin)

    return urdu, eng, roman,


if __name__ == "__main__":
    sext = ["Nice","bad"]
    text = ["میں معافی چاہتا ہوں", "میں ٹھیک ہوں","I am fine","Video achi hai","😂"]
    # text = "میں معافی چاہتا ہوں"
    # senti=urduconversion(text)
    print (detectlan(text))
    # print(clean_emoji)
    # extraction(text)
    # urduText = urduconversion(urdu)
    # print(sentiment_analysis(sext))
    # print(positive)
    # print(negative)
    # print(neutral)
    # print(eng)
