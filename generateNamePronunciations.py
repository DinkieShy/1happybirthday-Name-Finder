from urllib.request import urlopen
from string import ascii_lowercase
import re

def getNames():
	names = []
	unfilteredNames = []

	for char in ascii_lowercase:
		# Get the raw HTML
		url = "https://www.1happybirthday.com/fyn/" + char
		page = urlopen(url)
		html = page.read().decode("utf-8")

		# Extract just the divs with the names
		contentArea = html[html.find("<div id=\"content_block\">"):html.find("<div id=\"right_column\">")]
		# Search through each line- lines beginning with "<a" have names, extract just the innerHTML part
		unfilteredNames = unfilteredNames + [(item[item.find(">")+1:-10] if item[:2] == "<a" else None) for item in contentArea.split("\n")]

	# Lines that don't start with "<a" resulted in None being added to the array
	# Some names have "NEW" or "2" at the end
	# These all need to be filtered (NEW/2 are kept for finding the URL again later)
	for name in unfilteredNames:
		if name != None:
			names.append([name, re.sub(r'[0-9]', "", name.replace("NEW", ""))])

	# This array contains [url appropriate name, pronouncable name]
	return names

def main():
	# Get list of names from 1happybirthday
	# Generate pronunciations
	# Save to reasonable JSON structure

	names = getNames()

	print(len(names))

if __name__ == "__main__":
	main()
