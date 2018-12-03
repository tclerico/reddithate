# reddithate
First Place Ithaca College Code-a-thon project
This project makes use of the reddit python api (praw) and the google cloud natural language processor
to extract comments and posts from reddit and analyze them for connotaion and subject matter. They are then assocaited with
the user that posted them and the subreddit they are posted in.
All data is dumped into a MySQL database while aggregating data and a snap shot can be taken at any point to 
move all the data to a Neo4J Database for better visualizations.
