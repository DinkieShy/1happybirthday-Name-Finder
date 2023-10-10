import os
from g2p_en import G2p
from cmudict import phones as cmuDictPhones
import re
from json import load
from tqdm import tqdm

def isValidPhone(phone):
	validPhones = cmuDictPhones()
	phone = re.sub(r'[0-9]', "", phone)
	for i in validPhones:
		if phone == i[0]:
			return True
	return False

def comparePronunciations(actual, target):
	total = len(actual) if len(actual) >= len(target) else len(target)
	score = 0
	score -= abs(len(actual) - len(target))
	for (a, b) in zip(target, actual):
		if a == b:
			score += 1
		else:
			score -= 1
	return score

def getBestMatch(name, pronunciation):
	with open("pronunciations.json", "r") as file:
		storedNames = load(file)

	print("Searching...")
	exactMatches = []
	for key in tqdm(list(storedNames.keys())):
		if storedNames[key]["filtered"] == name: exactMatches.append(key)
		elif storedNames[key]["pronunciation"] == pronunciation: exactMatches.append(key)

	if len(exactMatches) >= 1:
		print("Exact match found!")
		return exactMatches

	print("Exact match not found, searching for close pronunciations...")
	bestMatches = []
	for nameKey in tqdm(list(storedNames.keys())):
		score = comparePronunciations(storedNames[nameKey]["pronunciation"], pronunciation)
		bestMatches.append((nameKey, score))
		if len(bestMatches) > 5:
			bestMatches = sorted(bestMatches, key=lambda match: match[1], reverse=True)
			bestMatches.pop()

	return bestMatches

def main():
	assert os.path.isfile("pronunciations.json"), "Couldn't find the pronunciations file!"

	g2p = G2p()
	name = input("What name would you like to search for?").lower()
	pronunciation = [phone for phone in g2p(name)]

	response = input(f"Does this pronunciation look right? [Y/n]\n{pronunciation}\n")
	if response.lower() == "n":
		print("Type each phone and press return. Press return without typing to end")
		print("Type ? for a list of valid phones")
		pronunciation = []
		done = False
		while not done:
			nextPhone = input().upper()
			if nextPhone == "":
				response = input(f"Is this correct? [Y/n]\n{pronunciation}\n")
				if response.lower() == "n":
					pronunciation = []
					print("Resetting...")
				else:
					done = True
			elif nextPhone == "?": print("https://en.wikipedia.org/wiki/ARPABET")
			elif not isValidPhone(nextPhone): print("Invalid phone")
			else: pronunciation.append(nextPhone)

	bestMatches = getBestMatch(name, pronunciation)
	print(bestMatches)

if __name__ == "__main__":
	main()
