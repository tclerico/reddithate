import praw
import datetime
import os
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from environset import *
from mysqlstuff import *
# from neo import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from text_analysis import *

scheduler = BackgroundScheduler()


def get_data(subreddits, postCount):

    set_praw()

    reddit = praw.Reddit(client_id=os.environ.get("CLIENT_ID"),
                         client_secret=os.environ.get("CLIENT_SECRET"),
                         user_agent='Get Data by /u/IthacaCompSci')

    print("Connection read only to reddit: " + str(reddit.read_only))
    print()

    for sr in subreddits:

        subreddit = reddit.subreddit(sr)

        print("Sub-Reddit: " + subreddit.display_name)


        for submission in subreddit.hot(limit=postCount):

            posts = []
            comments = []

            # get all info about the post
            # adds all posts whether they match a subject or not
            print(submission.title)
            print("post id: "+submission.id)
            print("posted by: "+ submission.author.name)
            post_info = {
                "subreddit_id":     submission.subreddit_id[3:],
                "subreddit":        subreddit.display_name,
                "post_id":          submission.id,
                "author":           submission.author.name,
                "author_id":        reddit.redditor(str(submission.author)).id,
                "date":             datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "title":            submission.title,
                "karma":            submission.score,
                "vote_ratio":       submission.upvote_ratio,
                "link":             submission.url
            }
            text = submission.selftext
            post_subject = find_subject(text)
            if len(post_subject) > 0:
                print("Adding subject id for post")
                post_info['subject_id'] = post_subject[0][1]
            post_info['sentiment'] = text_sentiment(text)

            posts.append(post_info)



            # go through all comments in the post
            submission.comments.replace_more(limit=None)
            for comment in submission.comments:
                # make sure comment is actually there
                if comment.body != "[removed]" and comment.body != '[deleted]':
                    # need try/except for edge cases (eg. account is deleted)
                    try:
                        # analyze comment before adding it -> if it doesn't match a subject, don't add it
                        comment_subject = find_subject(comment.body)
                        if len(comment_subject) > 0:
                            # get all info from comments and add to list
                            print("comment id: "+comment.id+" in post: "+comment.submission.id)
                            print("subject: "+str(comment_subject[0][1]))
                            info = {
                                'post_id': comment.submission.id,
                                'comment_id': comment.id,
                                'permalink': comment.permalink,
                                'author': comment.author.name,
                                'author_id': reddit.redditor(str(comment.author)).id,
                                'date': datetime.datetime.fromtimestamp(comment.created_utc).strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                                'body': comment.body,
                                'score': comment.score,
                                'parent_id': (comment.parent_id if str(comment.parent_id)[:2] != "t3" else 'NULL'),
                                'subject_id': comment_subject[0][1],
                                'sentiment': text_sentiment(comment.body)
                            }
                            comments.append(info)
                    except:
                        continue
            print("Comments done, adding post and comments to DB")
            insert_post(posts)
            insert_comment(comments)




def main():
    subreddits = [
        "politics",
        "thedonald"
    ]
    posts = 3
    get_data(subreddits, posts)
main()