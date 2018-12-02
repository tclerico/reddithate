import praw
import datetime
import os
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from environset import *
from mysqlstuff import *
from neo import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

def get_data_from_subreddit():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str('/Users/timc/Desktop/redditNLP-c250299d83e5.json')
    # Instantiates a client
    client = language.LanguageServiceClient()

    set_praw()

    reddit = praw.Reddit(client_id=os.environ.get("CLIENT_ID"),
                         client_secret=os.environ.get("CLIENT_SECRET"),
                         user_agent='Get Data by /u/IthacaCompSci')

    print("Connection read only to reddit: " + str(reddit.read_only))
    print()

    # assume you have a Reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit('thedonald')

    print("Sub-Reddit: "+subreddit.display_name)  # Output: redditdev

    # empty list to add all comments into
    post_comments = []
    posts = []


    # assume you have a Subreddit instance bound to variable `subreddit`
    for submission in subreddit.hot(limit=3):
        print("Post: "+ submission.title)
        post_info = {
            "subreddit_id" : submission.subreddit_id[3:],
            "subreddit": subreddit.display_name,
            "post_id" : submission.id,
            "author": submission.author.name,
            "author_id": reddit.redditor(str(submission.author)).id,
            "date": datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "title": submission.title,
            "karma": submission.score,
            "vote_ratio": submission.upvote_ratio,
            "link": submission.url
        }
        text = submission.title
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT
        )
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        post_info["sentiment"] = sentiment.score
        #print(post_info)
        posts.append(post_info)

        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if comment.body != "[removed]" and comment.body != '[deleted]':
                # get all info from comments and add to list
                try:
                    # print(comment.author.name)
                    info = {
                        'post_id': comment.submission.id,
                        'comment_id': comment.id,
                        'permalink': comment.permalink,
                        'author': comment.author.name,
                        'author_id': reddit.redditor(str(comment.author)).id,
                        'date': datetime.datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'body': comment.body,
                        'score': comment.score,
                        'parent_id': (comment.parent_id if str(comment.parent_id)[:2] != "t3" else 'NULL')
                    }
                    text = comment.body
                    document = types.Document(
                        content=text,
                        type=enums.Document.Type.PLAIN_TEXT
                    )
                    sentiment = client.analyze_sentiment(document=document).document_sentiment
                    info["sentiment"] = sentiment.score
                    post_comments.append(info)
                except:
                    continue

        print("Comments done")
        print()
        #print(post_comments)
        results = [posts, post_comments]
        return results


def update_sentiments():
    average_sentiments()




print("Starting MySQL Inserts")
print()

results = get_data_from_subreddit()
# Insert data into MySQL
insert_post(results[0])
insert_comment(results[1])

p = scheduler.add_job(update_sentiments, CronTrigger.from_crontab('0 * * * *'))


# print("Starting Neo4j Node Creation")
# print()
# Create nodes in neo4J with MySQL info
# Pulls entire MySQL db -> only use when neo4j is clear or db has unique data
neo4j_execute()
print("Nodes Created, Check Console")
