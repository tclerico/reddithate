'''
Created by Tim Clerico on Saturday December 1st
https://github.com/tclerico
'''

import mysql.connector
from mysql.connector import errorcode
from environset import *

try:
    # set_mysql() is a function for sensitive mysql database info
    # and is not included in the project
    connection = set_mysql()
    cnx = mysql.connector.connect(user=connection[0], password=connection[1], host=connection[2], database='reddit')

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Auth Error")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("database doesn't exist")
    else:
        print(err)


def insert_post(info):
    # create sql query
    cursor = cnx.cursor()
    for i in info:
        # create user if user id doesn't exist
        try:
            sql = "INSERT INTO users (id, name) VALUES (%s, %s)"
            val = (i.get('author_id'), i.get('author'))
            cursor.execute(sql, val)
        except:
            print("User already exists")

        # create subreddit if it doesn't already exist
        try:
            sql = "INSERT INTO subreddits (id, name) VALUES (%s, %s)"
            val = (i.get('subreddit_id'), i.get('subreddit'))
            cursor.execute(sql, val)
        except:
            print("Subreddit already exists")

        try:
            # insert post
            sql = "INSERT INTO posts (id, title, date, link, sentiment, karma, user_id, subreddit_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (i.get('post_id'), i.get('title'), i.get('date'), i.get('link'), i.get('sentiment'),
                   i.get('karma'), i.get('author_id'), i.get('subreddit_id'))
            cursor.execute(sql, val)
        except:
            print("Post already exists")

    cnx.commit()


def insert_comment(info):
    # create sql query
    cursor = cnx.cursor()
    count = 0
    for i in info:
        # create user if user id doesn't exist
        try:
            sql = "INSERT INTO users (id, name) VALUES (%s, %s)"
            val = (i.get('author_id'), i.get('author'))
            cursor.execute(sql, val)
        except:
            count+=1
        try:
            # insert comment
            sql = "INSERT INTO comments (id, body, date, link, karma, sentiment, user_id, post_id, subject_id, parent_id ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (i.get('comment_id'), i.get('body'), i.get('date'), i.get('permalink'), i.get('score'),
                   i.get('sentiment'), i.get('author_id'), i.get('post_id'), i.get('subject_id'), i.get('parent_id'))
            cursor.execute(sql, val)
        except:
            continue

    cnx.commit()
    print("There were "+str(count)+" users who made multiple comments")


def pull_all():

    cursor = cnx.cursor()

    users = "SELECT * FROM users"
    subreddits = "SELECT * FROM subreddits"
    subjects = "SELECT * FROM subjects"
    posts = "SELECT * FROM posts"
    comments = "SELECT * FROM comments"


    pull = dict()

    cursor.execute(users)
    pull["users"] = cursor.fetchall()
    cursor.execute(subreddits)
    pull["subreddits"] = cursor.fetchall()
    cursor.execute(subjects)
    pull["subjects"] = cursor.fetchall()
    cursor.execute(posts)
    pull["posts"] = cursor.fetchall()
    cursor.execute(comments)
    pull["comments"] = cursor.fetchall()


    return pull


def get_comment():
    cursor = cnx.cursor()

    sql = "Select * from comments"
    cursor.execute(sql)

    result = cursor.fetchall()

    return result


def get_subjects():
    cursor = cnx.cursor()

    subjects = "SELECT * FROM subjects"
    cursor.execute(subjects)
    return cursor.fetchall()


def update_user_averages():
    cursor = cnx.cursor()

    users=get_users()

    uavg = []

    for u in users:
        try:
            sql = "Select SUM(sentiment), count(sentiment) from comments where user_id = %(id)s"
            cursor.execute(sql, {"id": u})
            inf = cursor.fetchall()[0]
            cavg = inf[0]/inf[1]
        except:
            continue

        uavg.append([u, cavg])
    return uavg


def update_subreddit_average():
    cursor = cnx.cursor()

    sql = "select sum(c.sentiment), count(sentiment), ps.sid from comments as c inner join (select p.id as pid, s.id as sid, s.name from posts as p inner join subreddits as s where p.subreddit_id=s.id) as ps where c.post_id = ps.pid Group by ps.sid;"
    cursor.execute(sql)
    query = cursor.fetchall()
    ravg = []
    for q in query:
        avg = q[0]/q[1]
        ravg.append([q[2], avg])

    return ravg


def get_users():
    cursor = cnx.cursor()
    sql = "Select id from users;"
    cursor.execute(sql)
    query = cursor.fetchall()
    result = []
    for q in query:
        result.append(q[0])
    return result


def av_test():
    user = get_users()
    u = user[0]
    print(u)
    cursor = cnx.cursor()
    sql = "Select SUM(sentiment), count(sentiment) from comments where user_id = %(user_id)s"
    cursor.execute(sql, {'user_id': u})
    print(cursor.fetchall()[0])


def insert_subjects(subjects):
    cursor = cnx.cursor()
    counter = 20
    for s in subjects:
        sql = "INSERT INTO subjects (id, name) VALUES (%s, %s)"
        cursor.execute(sql, (counter, s))
        counter+=1
    cnx.commit()

# def main():
#     s = [
#         'politics',
#         'politician',
#         'rally',
#         'alt-right',
#         'college',
#         'senate',
#         'representatives',
#         'congress',
#         'news'
#     ]
#     insert_subjects(s)
# main()