import os
import pymongo
import feedparser
import arrow
import datetime
from dateutil.parser import parse
from bson.objectid import ObjectId
import Queue
import threading

MONGOHQ_URL = os.environ.get("MONGOHQ_URL")
if MONGOHQ_URL:
	conn = pymongo.Connection(MONGOHQ_URL)
	db = conn[urlparse(MONGOHQ_URL).path[1:]]
else:
	# Not on an app with the MongoHQ add-on, do some localhost action
    conn = pymongo.Connection('localhost')
    db = conn['rss-rdr']	

queue = Queue.Queue()

class ThreadFetchPosts(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			#grab feed from the queue
			feed = self.queue.get()

			self.fetch_and_save_posts(feed)

			self.queue.task_done()

	def fetch_and_save_posts(self, feed):
		print "[+] FEED ID: ", feed.get("_id")
		print "[+] FEED: ", feed.get("title")
		data = feedparser.parse(feed.get("xmlUrl"))
		# data = feedparser.parse("http://feeds.feedburner.com/mobbit/TnEX")
		print "[+] Entries ", len(data.entries)
		posts = []
		feed_ranks = []
		for item in data.entries:
			post = {
				"group": feed.get("group"),
				"feed_id": ObjectId(feed.get("_id")),
				"title" : item.get("title"),
				# "description": item.description,
				"link": item.get("link"),
				"read" : False,
				"created": datetime.datetime.utcnow(),
				"tags": [],
				"starred" : False
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
				print "[+] KEYS: ", item.keys()
				if "published" not in item:
					post["published"] = None
				else:		
					print parse(item["published"])
					post["published"] = parse(item["published"])
							
			posts.append(post)	

		if len(posts) > 0:	
			db["posts"].insert(posts)

def execute():
	db["posts"].remove()
	db["ranks"].remove()

	# feeds = db["feeds"].find({"group": "Others"})
	# feeds = db["feeds"].find({"group": "Live Journal"})
	feeds = db["feeds"].find()

	for i in range(50):
		t = ThreadFetchPosts(queue)
		t.setDaemon(True)
		t.start()

	for feed in feeds:
		queue.put(feed)

	queue.join()
	print "[+] STOPPED!"		


if __name__ == "__main__":
	execute()