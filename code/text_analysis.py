import os
import re
from textblob import TextBlob
from mysqlstuff import *


def convert_to_set(text):
    wordList = re.sub("[^\w]", " ", text).split()
    for x in range(0, len(wordList)):
        wordList[x] = wordList[x].lower()
    return set(wordList)


def find_subject(text):
    tCompare = convert_to_set(text)
    subjects = get_subjects()

    possible=[]
    for s in subjects:
        if s[1] in tCompare:
            possible.append([s[1], s[0]])

    # for now just takes first found subject
    # TODO Better way to determine comments subject

    return possible[0]


def text_sentiment(text):
    to_analise = TextBlob(text)
    score = to_analise.sentiment
    return score.polarity

