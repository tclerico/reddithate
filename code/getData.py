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

scheduler = BackgroundScheduler()

def get_data_from_subreddit(subreddits, postCount):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str('redditNLP-c250299d83e5.json')
    # Instantiates a client
    client = language.LanguageServiceClient()

    set_praw()

    reddit = praw.Reddit(client_id=os.environ.get("CLIENT_ID"),
                         client_secret=os.environ.get("CLIENT_SECRET"),
                         user_agent='Get Data by /u/IthacaCompSci')

    print("Connection read only to reddit: " + str(reddit.read_only))
    print()

    for subredditToSearch in subreddits:
        # assume you have a Reddit instance bound to variable `reddit`
        subreddit = reddit.subreddit(subredditToSearch)

        print("Sub-Reddit: "+subreddit.display_name)  # Output: redditdev

        # empty list to add all comments into
        post_comments = []
        posts = []

        subjects = get_subjects()

        # assume you have a Subreddit instance bound to variable `subreddit`
        for submission in subreddit.hot(limit=postCount):
            # TODO: check if submission entities match subject


            print("Post: "+ submission.title)
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
            text = submission.title
            print(text)

            document = types.Document(
                content=text,
                type=enums.Document.Type.PLAIN_TEXT
            )

            found = False
            for word in text.split():
                for subject in subjects.get("subjects"):
                    if word.lower() in subject[1].lower():
                        if not found:
                            id = subject[0]
                            print(id)
                            print()
                            post_info["subject_id"] = id
                            found = True
                            # TODO: WE FOUND A MATCH ADD THE RECORD

                            sentiment = client.analyze_sentiment(document=document).document_sentiment
                            post_info["sentiment"] = sentiment.score
                            # print(post_info)
                            posts.append(post_info)

                            submission.comments.replace_more(limit=None)
                            for comment in submission.comments.list():
                                if comment.body != "[removed]" and comment.body != '[deleted]':
                                    # get all info from comments and add to list
                                    try:
                                        # TODO: check if entities match subjects

                                        # print(comment.author.name)
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
                                            'parent_id': (comment.parent_id if str(comment.parent_id)[:2] != "t3" else 'NULL')
                                        }
                                        text = comment.body
                                        document = types.Document(
                                            content=text,
                                            type=enums.Document.Type.PLAIN_TEXT
                                        )

                                        comment_found = False
                                        for comment_word in text.split():
                                            for comment_subject in subjects.get("subjects"):
                                                if comment_word.lower() in comment_subject[1].lower():
                                                    if not comment_found:
                                                        comment_id = subject[0]
                                                        print(comment_id)
                                                        info["subject_id"] = comment_id
                                                        comment_found = True
                                                        # TODO: WE FOUND A MATCH ADD THE RECORD
                                                        sentiment = client.analyze_sentiment(document=document).document_sentiment
                                                        info["sentiment"] = sentiment.score
                                                        post_comments.append(info)

                                    except:
                                        continue

                            print("Comments done")
        insert_post(posts)
        print(post_comments)
        insert_comment(post_comments)





def main():
    # List of all subreddits to search
    subreddits = {}

    # How many posts to search
    postCount = 10

    get_data_from_subreddit(subreddits, postCount)

main()