import pymongo
import feedparser
import arrow
import datetime
from bson.objectid import ObjectId

conn = pymongo.Connection('localhost')
db = conn['rss-rdr']	


flex_feeds = db["feeds"].find({"group" : "Popular"})

for feed in flex_feeds:
	print "[+] FEED ID: ", feed.get("_id")
	data = feedparser.parse(feed.get("xmlUrl"))
	print "[+] Entries ", len(data.entries)
	posts = []
	for item in data.entries:
		post = {
			"feed_id": ObjectId(feed.get("_id")),
			"title" : item.title,
			"description": item.description,
			"link": item.link,
			"read" : False,
			"created": datetime.datetime.utcnow()
		}
		if item.has_key("updated_parsed"):
			post["published"] = datetime.datetime(item.updated_parsed[0], 
				item.updated_parsed[1], 
				item.updated_parsed[2],
				item.updated_parsed[3], 
				item.updated_parsed[4]) 
		elif item.has_key("published_parsed"):	
			post["published"] = datetime.datetime(item.published_parsed[0], 
				item.published_parsed[1], 
				item.published_parsed[2],
				item.published_parsed[3], 
				item.published_parsed[4]) 
		posts.append(post)	

	db["posts"].insert(posts)	