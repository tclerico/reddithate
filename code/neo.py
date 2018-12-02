'''
Created by Tim Clerico on Saturday December 1st
https://github.com/tclerico
'''

from neo4j import GraphDatabase
from mysqlstuff import *
import os
from environset import *

uri = "bolt://localhost:7687"
set_pass()
password = os.environ.get("PASSWORD")
driver = GraphDatabase.driver(uri, auth=("neo4j", password))


def create_nodes(tx):
    info = pull_all()

    # Users
    for usr in info.get("users"):
        tx.run("Create (:User {name: $name, id: $id})", name=usr[1], id=usr[0])

    # Subreddits
    for sub in info.get("subreddits"):
        tx.run("Create (:SubReddit {name: $name, id: $id})", name=sub[1], id=sub[0])

    # Subjects
    # for s in info.get("subject_id"):
    #     tx.run("Create (:Subject {name: $name, id: $id})", name=s[1], id=s[0])

    # Posts
    for p in info.get("posts"):
        tx.run("Create (:Post {title: $title, id: $id, date: $date, sentiment: $sentiment,"
               " karma: $karma, user_id: $uid, subreddit_id: $sub_id, subject_id: $subject_id})",
               title=p[1], id=p[0], date=p[2], sentiment=p[4], karma=p[5], uid=p[6], sub_id=p[7], subject_id=p[8])

    # Comments
    for c in info.get("comments"):
        tx.run("Create (:Comment {id: $id, body: $body, date: $date, karma: $karma, sentiment: $sentiment,"
               "user_id: $uid, post_id: $pid, subject_id: $sid, parent_id: $parent_id})",
               body=c[1], id=c[0], date=c[2], karma=c[4], sentiment=c[5], uid=c[6], pid=c[7], sid=c[8], parent_id=c[9])


def set_indices(tx):
    # Create indices for user
    tx.run("Create INDEX ON :User(name)")
    tx.run("Create INDEX ON :User(id)")

    # Create indices for subreddits
    tx.run("Create INDEX ON :SubReddit(name)")
    tx.run("Create INDEX ON :SubReddit(id)")

    # Create indicies for subjects
    # tx.run("CREATE INDEX ON :Subject(name)")
    # tx.run("CREATE INDEX ON :Subject(id)")

    # Create indices for Posts
    tx.run("Create index on :Post(id)")
    tx.run("Create index on :Post(date)")
    tx.run("Create index on :Post(sentiment)")
    tx.run("create index on :Post(user_id)")
    tx.run("create index on :Post(subreddit_id)")

    # Create indices for Comments
    tx.run("Create index on :Comment(id)")
    tx.run("Create index on :Comment(date)")
    tx.run("Create index on :Comment(sentiment)")
    tx.run("create index on :Comment(user_id)")
    tx.run("create index on :Comment(post_id)")

def simple_relationships(tx):
    tx.run("match (u:User), (p:Post) where u.id=p.user_id Create (u)-[:Posted]->(p)")
    tx.run("match (u:User), (c:Comment) where u.id=c.user_id Create (u)-[:Commented]->(c)")
    tx.run("match (p:Post), (c:Comment) where p.id=c.post_id Create (c)-[:Comment_of]->(p)")
    tx.run("MATCH (p:Post), (s:SubReddit) WHERE p.subreddit_id=s.id CREATE (p)-[:Posted_In]->(s)")
    # tx.run("match (c:Comments), (s:Subjects) WHERE c.subject_id=s.id CREATE (c)-[:About]->(s)")

# def neo4j_execute():
#     with driver.session() as session:
#         print("Creating Nodes")
#         session.write_transaction(create_nodes)
#         print("Creating Indices")
#         session.write_transaction(set_indices)
#         print("Creating realtionships")
#         session.write_transaction(simple_relationships)

with driver.session() as session:
    with driver.session() as session:
        session.write_transaction(create_nodes)
        session.write_transaction(set_indices)
        session.write_transaction(simple_relationships)