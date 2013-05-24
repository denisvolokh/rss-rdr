import pymongo
import feedparser
import arrow
import datetime
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING


def main():
	conn = pymongo.Connection('localhost')
	db = conn['rss-rdr']	
	feeds = db["feeds"].find({"group": "Others"})
	# feeds = db["feeds"].find({"group": "Others", "title" : "Lifehacker"})
	# feeds = db["feeds"].find()

	for feed in feeds:
		print "---"*10
		print "[+] FEED: ", feed.get("title")
		last_post = None
		latests_post = db["posts"].find({"feed_id" : feed["_id"]}).sort("published", DESCENDING)
		print latests_post.count()
		if latests_post.count() > 0:
			last_post = latests_post[0]

		data = feedparser.parse(feed.get("xmlUrl"))
		print "[+] Entries ", len(data.entries)	
		posts = []
		for item in data.entries:
			if last_post is not None: 
				if last_post["title"] == item.get("title"):		
					print "[-] NO NEW POSTS!"
					print "LAST TITLE: ", last_post["title"] 
					break
				else:
					print "[++++++] FOUND NEW!!!"
					print "LAST TITLE: ", last_post["title"] 
					print "NEW TITLE: ", item.get("title") 
					posts.append(parse_post(item, feed))	

		if len(posts) > 0:	
			db["posts"].insert(posts)	

	db["tags"].insert([
		{"name" : "job"},{"name" : "kids"},{"name" : "hobby"},{"name" : "family"}
	])	


def parse_post(item, feed):
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
	return post		


if __name__ == "__main__":
	main()	
