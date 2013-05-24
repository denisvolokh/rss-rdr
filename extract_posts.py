import pymongo
import feedparser
import arrow
import datetime
from bson.objectid import ObjectId

conn = pymongo.Connection('localhost')
db = conn['rss-rdr']	


db["posts"].remove()
db["tags"].remove()
flex_feeds = db["feeds"].find({"group": "Others"})

for feed in flex_feeds:
	print "[+] FEED ID: ", feed.get("_id")
	print "[+] FEED: ", feed.get("title")
	data = feedparser.parse(feed.get("xmlUrl"))
	# data = feedparser.parse("http://feeds.feedburner.com/mobbit/TnEX")
	print "[+] Entries ", len(data.entries)
	posts = []
	for item in data.entries:
		post = {
			"group": feed.get("group"),
			"feed_id": ObjectId(feed.get("_id")),
			"title" : item.get("title"),
			# "description": item.description,
			"link": item.get("link"),
			"read" : False,
			"created": datetime.datetime.utcnow(),
			"tags": []
		}

		if item.has_key("description"):
			post["content"] = item["description"]
		elif item.has_key("content"):
			post["content"] = item["content"]	

		if item.has_key("updated_parsed"):
			post["published"] = datetime.datetime(item.updated_parsed[0], 
				item.updated_parsed[1], 
				item.updated_parsed[2],
				item.updated_parsed[3], 
				item.updated_parsed[4]) 
		elif item.has_key("published_parsed"):	
			if item.published_parsed:
				post["published"] = datetime.datetime(item.published_parsed[0], 
					item.published_parsed[1], 
					item.published_parsed[2],
					item.published_parsed[3], 
					item.published_parsed[4]) 
			elif "published" in item:
				post["published"] = item["published"]
			else:
				post["published"] = datetime.utcnow()
						
		posts.append(post)	

	if len(posts) > 0:	
		db["posts"].insert(posts)	

	db["tags"].insert([
		{"name" : "job"},{"name" : "kids"},{"name" : "hobby"},{"name" : "family"}
	])	
