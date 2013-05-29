import pymongo
import feedparser
import arrow
import datetime
from dateutil.parser import parse
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING
from urlparse import urlparse
import os

MONGOHQ_URL = os.environ.get("MONGOHQ_URL")
if MONGOHQ_URL:
	conn = pymongo.Connection(MONGOHQ_URL)
	db = conn[urlparse(MONGOHQ_URL).path[1:]]
else:
	# Not on an app with the MongoHQ add-on, do some localhost action
    conn = pymongo.Connection('localhost')
    db = conn['rss-rdr']	

def post_date(item):
	if item.has_key("updated_parsed"):
		published = datetime.datetime(item.updated_parsed[0], 
			item.updated_parsed[1], 
			item.updated_parsed[2],
			item.updated_parsed[3], 
			item.updated_parsed[4]) 
	elif item.has_key("published_parsed") and item.published_parsed:
		published = datetime.datetime(item.published_parsed[0], 
				item.published_parsed[1], 
				item.published_parsed[2],
				item.published_parsed[3], 
				item.published_parsed[4]) 
	else:
		published = datetime.datetime.utcnow()
	return published	

def main():
	conn = pymongo.Connection('localhost')
	db = conn['rss-rdr']	
	feeds = db["feeds"].find({"group": "Mac"})
	# feeds = db["feeds"].find({"title" : ""})
	# feeds = db["feeds"].find({"_id" : ObjectId("519f16b59929258dda9b82c9")})
	# feeds = db["feeds"].find()

	for feed in feeds:
		posts = []
		data = feedparser.parse(feed.get("xmlUrl") + "?" + str(datetime.datetime.utcnow().microsecond))

		print "---"*10
		print "[+] FEED: ", feed.get("title")
		last_post = None
		latests_posts = db["posts"].find({"feed_id" : feed["_id"]}).sort("published", DESCENDING)
		if latests_posts.count() == 0:
			# Add All Entries
			for new_entry in data.entries:
				posts.append(parse_post(new_entry, feed))
				update_feed_rank(feed)
		else:
			# Check for new entries
			latest_one_post = latests_posts[0]
			print "[+] last_post feed id: ", latest_one_post["feed_id"] 
			print "[+] last date: ", latest_one_post["published"]
			if latest_one_post["published"] is not None:
				# check entries by date
				for new_entry in data.entries:
					parsed_post = parse_post(new_entry, feed)
					if latest_one_post["published"] < parsed_post["published"]:
						posts.append(parsed_post)
						update_feed_rank(feed)
						print "[+] Added new post"
						print "[+] parsed post date: ", parsed_post["published"]
					else:
						break	
			else:
				#check entries by title
				print "[+] Checking titles...."
				print "[+] Latest title from db: ", latest_one_post["link"] 	
				for new_entry in data.entries:
					parsed_post = parse_post(new_entry, feed)
					existing_post_with_link = db["posts"].find_one({"feed_id" : feed["_id"], "link" : parsed_post["link"]})
					if existing_post_with_link is None:
						print "[+] Added new post"
						posts.append(parsed_post)
						update_feed_rank(feed)

		if len(posts) > 0:
			print "[+] INSERT RECORDS: ", len(posts)
			db["posts"].insert(posts)					

def update_feed_rank(feed):
	feed_rank = db["feeds"].find_one({"_id": feed["_id"]})
	db["feeds"].update({"_id" : feed_rank["_id"]}, {"$set" : {"count": feed_rank["rank"] + 1}})


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
	elif item.has_key("published_parsed") and item.published_parsed:
		post["published"] = datetime.datetime(item.published_parsed[0], 
				item.published_parsed[1], 
				item.published_parsed[2],
				item.published_parsed[3], 
				item.published_parsed[4]) 
	else:
		# print "[+] KEYS: ", item.keys()
		if "published" not in item:
			post["published"] = None
		else:		
			print parse(item["published"])
			post["published"] = parse(item["published"])
	
	if post["published"] is not None:
		post["published"] = post["published"].replace(tzinfo=None)			
	return post		


if __name__ == "__main__":
	main()	
