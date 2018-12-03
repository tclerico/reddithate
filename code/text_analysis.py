import os
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from mysqlstuff import *


def find_subject(text):
    subjects = get_subjects()

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str('/Users/timc/Desktop/redditNLP-c250299d83e5.json')
    # Instantiates a client
    client = language.LanguageServiceClient()

    # The text to analyze
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    s = client.analyze_sentiment(document)
    sentiment = s.document_sentiment

    # Detects the sentiment of the text
    props = client.analyze_entities(document).entities

    possible = []
    # print(props)
    for s in subjects:
        for p in props:
            if p.name.lower() in s[1].lower():
                sid = s[0]
                possible.append([p,sid])

    if len(possible) > 1:
        top = [possible[0]]
        for s in range(1, len(possible)):
            f = possible[s][0].salience
            if f > top[0][0].salience:
                top[0] = possible[s]
        return top
    else:
        return possible


def text_sentiment(text):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str('/Users/timc/Desktop/redditNLP-c250299d83e5.json')
    # Instantiates a client
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    sentiment = client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score
