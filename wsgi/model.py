from pymongo import MongoClient
import json
import datetime
from tags import (
    parse_tags, 
    inc_tags, 
    update_tags,
    dec_tags
)
import os
import re
client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
db = client.blog

def sluggize(title):
        # Transform the title in an url friendly string
        return re.sub('[^\w]+', '-', title.lower())

def count_articles(tag=""):
        if tag:
            return db.articles.find({"tags":tag}).count()
        else:
            return db.articles.count()

def get_article(id):
        # Get an article provided its id
	articles = db.articles
	return articles.find_one({"id":id})

def get_articles(page, per_page=5, tag=""):
        # Return all articles containing a specific tag
        if tag:
            return db.articles.find({"tags":tag}).sort("_id",-1)
        else:
            return db.articles.find().sort("_id",-1).skip((page-1)*per_page).limit(per_page)

def get_tags():
        # Return all the tags with at least one occurrence, sorted by occurrence count
        return db.tags.find({ "count": { "$gt":0  } }).sort("count", -1)

def get_last_id():
	#Return the highest post ID from a MongoDB search
	# TODO: Not great... do that better
	if db.articles.count() == 0:
		return 0
	else:
		return db.articles.find().sort("_id", -1)[0]["id"]

def new_post(title, abstract, content,tags):
        # Create a new article given all the parameters
	post = {}
	post["title"] = title
	post["abstract"] = abstract
	post["content"] = content
        post["tags"] = parse_tags(tags)
        post["draft"] = True
        post["date"] = datetime.datetime.now().strftime("%d %B, %Y")
	post["id"] = sluggize(title)
	db.articles.save(post)
        inc_tags(tags, db)

def edit_post(title, abstract, content, tags, article):
        # Edit an article
	id = article["_id"]
        update_tags(article["tags"], parse_tags(tags), db)
	db.articles.update({"_id":id},{"$set": {"title":title, "abstract":abstract, "content":content,"tags":parse_tags(tags)}})

def del_article(id):
        # Delete an article
        dec_tags(get_article(id), db)
	db.articles.remove({"id":id})

def publish(article):
        # Publish an article, making it visible to everyone
        db.articles.update({"_id":article["_id"]},{"$set": {"draft":False}})

def unpublish(article):
        # Unpublish an article, making it invisible for anyone not logged
        db.articles.update({"_id":article["_id"]},{"$set": {"draft":True}})
