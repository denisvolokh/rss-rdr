import feedparser

def main():
	d = feedparser.parse('http://d3.ru/rss/all/popular/')
	print len(d.entries)
	for item in d.entries:
		print "-"*20
		print item.title
		print item.description
		print item.link
		if item.has_key("published"):
			print item.published

if __name__ == "__main__":
	main()	