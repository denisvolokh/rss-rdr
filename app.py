import os
from flask import Flask, Response, request, redirect, render_template, send_from_directory, send_file
from bs4 import BeautifulSoup
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo

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

@app.route("/api/digest")
def list_digest():
	unread_feed_ids = db["posts"].find({"read": False}).distinct("feed_id")
	
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

@app.route("/api/posts/make_read/<post_id>", methods=["POST", "GET"])
def post_make_read(post_id):
	# post_id = request.args["post_id"]
	db["posts"].update({"_id" : ObjectId(post_id)},{"$set" : {"read": True}})

	return dumps(dict(result=True))		

@app.route("/api/feeds")
def list_feeds():
    records = db["feeds"].find()

    feeds = []
    group = ""
    items = None
    for record in records:
    	unread_posts_count = db["posts"].find({"feed_id" : record.get("_id"), "read":False}).count()
    	if group != record.get("group"):
    		group = record.get("group")
    		if items:
    			feeds.append(items)
    		items = {
    			"group" : record.get("group"),
    			"items" : [{
    				"id": record.get("_id"),
    				"unread_count" : unread_posts_count,
    				"xmlUrl": record.get("xmlUrl"),
    				"htmlUrl": record.get("htmlUrl"), 
    				"title": record.get("title")
    			}]
    		}
    	else:
    		if items:
    			items["items"].append({
    				"id": record.get("_id"),
    				"unread_count" : unread_posts_count,
    				"xmlUrl": record.get("xmlUrl"),
    				"htmlUrl": record.get("htmlUrl"),  
    				"title" : record.get("title")	
    			})

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