from urllib.request import urlopen
from string import ascii_lowercase
import re
from g2p_en import G2p
from json import dump
from tqdm import tqdm

def getNames():
	names = []
	unfilteredNames = []

	print("Grabbing names...")
	for char in tqdm(ascii_lowercase):
		# Get the raw HTML
		url = "https://www.1happybirthday.com/fyn/" + char
		page = urlopen(url)
		html = page.read().decode("utf-8")

		# Extract just the divs with the names
		contentArea = html[html.find("<div id=\"content_block\">"):html.find("<div id=\"right_column\">")]
		# Search through each line- only lines beginning with "<a" have names, extract just the innerHTML part
		unfilteredNames = unfilteredNames + [(item[item.find(">")+1:-10]) for item in contentArea.split("\n") if item[:2] == "<a"]

	# Some names have "NEW" or "2" at the end
	# These all need to be filtered (NEW/2 are kept for finding the URL again later)
	for name in unfilteredNames:
		names.append([name.lower(), re.sub(r'[0-9]', "", name.replace("NEW", "")).lower()])

	print(f"Grabbed {len(names)} names")

	# This array contains [url appropriate name, pronouncable name]
	return names

def main():
	# Get list of names from 1happybirthday
	# Generate pronunciations
	# Save to reasonable JSON structure

	names = getNames()

	nameDict = {}

	print("Generating pronunciations...")
	g2p = G2p()
	for item in tqdm(names):
		pronunciation = [phone for phone in g2p(item[1])]
		nameDict[item[0]] = {"filtered": item[1], "pronunciation": pronunciation}

	print("Saving...")	
	with open("pronunciations.json", "w") as file:
		dump(nameDict, file)

	print("Done!")

if __name__ == "__main__":
	main()
