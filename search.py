import os
from g2p_en import G2p
from cmudict import phones as cmuDictPhones
import re
from json import load
from tqdm import tqdm
from sys import float_info

def isValidPhone(phone):
	validPhones = cmuDictPhones()
	phone = re.sub(r'[0-9]', "", phone)
	for i in validPhones:
		if phone == i[0]:
			return True
	return False

def comparePronunciations(guess, target):
	total = len(guess) if len(guess) >= len(target) else len(target)
	targetNoStress = [re.sub(r'[0-9]', "", phone) for phone in target]
	guessNoStress = [re.sub(r'[0-9]', "", phone) for phone in guess]
	score = 0

	rhymes = True if guessNoStress[-2:] == targetNoStress[-2:] else False
	firstSyllableMatch = True if guessNoStress[0] == targetNoStress[0] else False
	lengthMatch = True if len(guessNoStress) == len(targetNoStress) else False
	
	stressIndexGuess = [i for i in range(len(guess)) if re.sub(r'[A-Z]*', "", guess[i]) != "1"]
	stressIndexTarget = [i for i in range(len(target)) if re.sub(r'[A-Z]*', "", target[i]) != "1"]
	if len(stressIndexGuess) > 0 and len(stressIndexTarget) > 0:
		stressMatch = True if guess[stressIndexGuess[0]] == target[stressIndexTarget[0]] else False
	else: stressMatch = False

	if rhymes: score += 2
	if firstSyllableMatch: score += 2
	if lengthMatch: score += 1
	if stressMatch: score += 3

	return score

def getBestMatch(name, pronunciation):
	with open("pronunciations.json", "r") as file:
		storedNames = load(file)

	print("Searching...")
	exactMatches = []
	for key in tqdm(list(storedNames.keys())):
		if storedNames[key]["filtered"] == name: exactMatches.append((key, 0))
		elif storedNames[key]["pronunciation"] == pronunciation: exactMatches.append((key, 0))

	if len(exactMatches) >= 1:
		print("Exact match found!")
		return exactMatches

	print("Exact match not found, searching for close pronunciations...")
	bestMatches = []
	for nameKey in tqdm(list(storedNames.keys())):
		score = comparePronunciations(storedNames[nameKey]["pronunciation"], pronunciation)
		bestMatches.append((nameKey, score))
		if len(bestMatches) > 10:
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
	print(f"Here's the {len(bestMatches)} best matches I found! (in order)")
	for i in bestMatches:
		print(f"https://www.1happybirthday.com/play_song.php?name={i[0]}")

	input("Press return to exit")

if __name__ == "__main__":
	main()
