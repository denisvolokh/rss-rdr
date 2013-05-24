import os
from flask import Flask, Response, request, redirect, render_template, send_from_directory, send_file
from bs4 import BeautifulSoup
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
from urlparse import urlparse

#----------------------------------------
# initialization
#----------------------------------------

app = Flask(__name__)

app.config.update(
    DEBUG = True,
)

MONGOHQ_URL = os.environ.get("MONGOHQ_URL")
if MONGOHQ_URL:
	conn = pymongo.Connection(MONGOHQ_URL)
	db = conn[urlparse(MONGOHQ_URL).path[1:]]
else:
	# Not on an app with the MongoHQ add-on, do some localhost action
    conn = pymongo.Connection('localhost')
    db = conn['rss-rdr']	

#----------------------------------------
# controllers
#----------------------------------------

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/starred")
def list_starred():
	posts = db["posts"].find({"starred": True})
	
	return dumps(dict(result=True, posts=posts))


@app.route("/api/digest")
def list_digest():
	unread_feed_ids = db["posts"].find({"read": False}).distinct("feed_id")
	
	unread_feed_ids = unread_feed_ids[:5]

	print "[+] DIGEST len: ", len(unread_feed_ids)

	_records = []
	for feed_id in unread_feed_ids:
		feed = db["feeds"].find_one({"_id" : feed_id})
		unred_posts = db["posts"].find({"feed_id" : feed_id, "read" : False}).limit(1)
		for post in unred_posts:
			post["feed"] = feed
			_records.append(post)

	return dumps(dict(result=True, data=_records))


@app.route("/api/posts", methods=["POST", "GET"])
def list_posts():
	feed_id = request.args["feed_id"]
	feed = db["feeds"].find_one({"_id" : ObjectId(feed_id)})
	# unread_posts = db["posts"].find({"read": False, "feed_id" : ObjectId(feed_id)})
	posts = db["posts"].find({"feed_id" : ObjectId(feed_id)})

	return dumps(dict(result=True, data=posts, feed=feed))	

@app.route("/api/feeds/unread/count/<feed_id>", methods=["POST", "GET"])
def feeds_unread_count(feed_id):
	feed = db["feeds"].find_one({"_id" : ObjectId(feed_id)})
	count = db["posts"].find({"feed_id" : ObjectId(feed_id), "read" : False}).count()
	group_count = db["posts"].find({"group" : feed["group"], "read" : False}).count()

	return dumps(dict(result=True, unread_count=count, feed=feed_id, group_unread_count=group_count))		

@app.route("/api/posts/make_read/<post_id>", methods=["POST", "GET"])
def post_make_read(post_id):
	post = db["posts"].find_one({"_id" : ObjectId(post_id)})
	db["posts"].update({"_id" : ObjectId(post_id)},{"$set" : {"read": True}})

	feed = db["feeds"].find_one({"_id" : ObjectId(post["feed_id"])})
	count = db["posts"].find({"feed_id" : ObjectId(post["feed_id"]), "read" : False}).count()
	group_count = db["posts"].find({"group" : feed["group"], "read" : False}).count()

	return dumps(dict(result=True, unread_count=count, feed=post["feed_id"], group_unread_count=group_count))		


@app.route("/api/posts/update_star/<post_id>", methods=["UPDATE"])
def post_update_star(post_id):
	post = db["posts"].find_one({
		"_id" : ObjectId(post_id)
	})

	if post["starred"] == True:
		starred = False
	else:
		starred = True	

	db["posts"].update(
		{
			"_id" : ObjectId(post_id)
		},
		{
			"$set" : {"starred": starred}
		}
	)

	return dumps(dict(result=True))		


@app.route("/api/feed/make_read/<feed_id>", methods=["UPDATE"])
def feed_make_read_all(feed_id):
	feed = db["feeds"].find_one({"_id" : ObjectId(feed_id)})

	to_update = db["posts"].find({"feed_id" : ObjectId(feed_id), "read" : False})
	print "[+] LEN: ", to_update.count()

	db["posts"].update({"feed_id" : ObjectId(feed_id)}, {"$set" : {"read": True}}, multi=True)
	count = db["posts"].find({"feed_id" : ObjectId(feed_id), "read" : False}).count()
	print "[+] after: ", count

	group_count = db["posts"].find({"group" : feed["group"], "read" : False}).count()

	return dumps(dict(result=True, unread_count=count, feed=feed_id, group_unread_count=group_count))			

@app.route("/api/feed/unsubscribe/<feed_id>", methods=["DELETE"])
def feed_unsubscribe(feed_id):
	feed = db["feeds"].find_one({"_id" : ObjectId(feed_id)})
	db["feeds"].remove({"_id" : ObjectId(feed_id)})
	db["posts"].remove({"feed_id" : ObjectId(feed_id)})

	unread_posts_count_in_group = db["posts"].find({"group" : feed["group"], "read":False}).count()
	feeds_in_group = db["feeds"].find({"group" : feed["group"]})
	items = []
	for feed_item in feeds_in_group:
		items.append({
				"id": feed_item["_id"],
				"unread_count": db["posts"].find({"feed_id" : feed_item.get("_id"), "read":False}).count(),
				"xmlUrl": feed_item.get("xmlUrl"),
    			"htmlUrl": feed_item.get("htmlUrl"), 
    			"title": feed_item.get("title")
			})


	return dumps(dict(result=True, group={
			"group":feed["group"],
			"unread_count": unread_posts_count_in_group,
			"items": items
		}))		

@app.route("/api/feeds")
def list_feeds():
    records = db["feeds"].find()

    feeds = []
    group = ""
    items = None
    for record in records:
    	unread_posts_count = db["posts"].find({"feed_id" : record.get("_id"), "read":False}).count()
    	unread_posts_count_in_group = db["posts"].find({"group" : record["group"], "read":False}).count()
    	if group != record.get("group"):
    		group = record.get("group")
    		items = {
    			"group" : record.get("group"),
    			"unread_count": unread_posts_count_in_group,
    			"items" : [{
    				"id": record.get("_id"),
    				"unread_count" : unread_posts_count,
    				"xmlUrl": record.get("xmlUrl"),
    				"htmlUrl": record.get("htmlUrl"), 
    				"title": record.get("title")
    			}]
    		}
    		feeds.append(items)
    	else:
    		if items:
    			items["items"].append({
    				"id": record.get("_id"),
    				"unread_count" : unread_posts_count,
    				"xmlUrl": record.get("xmlUrl"),
    				"htmlUrl": record.get("htmlUrl"),  
    				"title" : record.get("title")	
    			})

    for feed in feeds:
    	print feed["group"]			
    			
    return dumps(dict(result=True, data=feeds))

@app.route("/api/upload", methods=['GET', 'POST'])
def upload():
	if request.method == "POST":
		file = request.files["file"]
		soup = BeautifulSoup(file.read(), "xml")
		outlines = soup.body.findAll(lambda tag: len(tag.attrs) == 2)
		subscriptions = dict({})

		print "[+] GROUPS: ", len(outlines)
		feeds = []

		for outline in outlines:
			print "[+] GROUP: ", outline["title"]
			for item in outline:
				feed = dict({})
				feed["group"] = outline["title"]
				item_soup = BeautifulSoup(str(item), "xml")
				item_soup_outline = item_soup.find("outline")
				if item_soup_outline != None:
					feed["title"] = item_soup_outline.get("title")
					feed["xmlUrl"] = item_soup_outline.get("xmlUrl")
					feed["htmlUrl"] = item_soup_outline.get("htmlUrl")
					feeds.append(feed)

			print "[+] ITEMS IN GROUP: ", len(feeds)		
		
		if len(feeds) > 0:
			db["feeds"].insert(feeds)	

	return dict(result=True)			
				
#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)