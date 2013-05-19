import sys
from bs4 import BeautifulSoup
# import Queue
import threading

# queue = Queue.queue()


def main():
	soup = BeautifulSoup(open("subscriptions.xml"), "xml")
	outlines = soup.body.findAll(lambda tag: len(tag.attrs) == 2)
	subscriptions = dict({})

	for outline in outlines:
		subscriptions[outline['title']] = []
		items = []
		for item in outline:
			# items.append(item)
			item_soup = BeautifulSoup(str(item), "xml")
			# print item_soup.find("outline")
			if item_soup.find("outline") != None:
				print item_soup.find("outline").get("title")	
			# print item_soup.get("title")
		# subscriptions[outline['title']] = items

	# print subscriptions.keys()
	# print subscriptions.keys()

if __name__ == "__main__":
	main()