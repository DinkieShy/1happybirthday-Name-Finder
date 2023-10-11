import os
from g2p_en import G2p
from cmudict import phones as cmuDictPhones
import re
from json import load
from tqdm import tqdm
from sys import float_info

def isValidPhone(phone):
	# Get list of valid phones from the CMU dictionary
	validPhones = cmuDictPhones()
	# Remove stress information
	phone = re.sub(r'[0-9]', "", phone)
	for i in validPhones:
		if phone == i[0]:
			return True
	return False

def comparePronunciations(guess, target):
	# Stresses don't matter for certain metrics like rhyming
	targetNoStress = [re.sub(r'[0-9]', "", phone) for phone in target]
	guessNoStress = [re.sub(r'[0-9]', "", phone) for phone in guess]

	# If last two syllables match, the words rhyme
	rhymes = True if guessNoStress[-2:] == targetNoStress[-2:] else False
	# The first syllable matching is important too
	firstSyllableMatch = True if guessNoStress[0] == targetNoStress[0] else False
	# The length doesn't matter too much, but any information is helpful
	lengthMatch = True if len(guessNoStress) == len(targetNoStress) else False
	
	# Find which syallables are stressed
	stressIndexGuess = [i for i in range(len(guess)) if re.sub(r'[A-Z]*', "", guess[i]) != "1"]
	stressIndexTarget = [i for i in range(len(target)) if re.sub(r'[A-Z]*', "", target[i]) != "1"]
	# Check to see if there's a match
	if len(stressIndexGuess) > 0 and len(stressIndexTarget) > 0:
		stressMatch = True if guess[stressIndexGuess[0]] == target[stressIndexTarget[0]] else False
	else: stressMatch = False

	# Assign score
	score = 0
	if rhymes: score += 2
	if firstSyllableMatch: score += 2
	if lengthMatch: score += 1
	if stressMatch: score += 3

	return score

def getBestMatch(name, pronunciation):
	# Load the giant list of names from the site
	with open("pronunciations.json", "r") as file:
		storedNames = load(file)

	print("Searching...")
	# First, check to see if the name straight up exists
	exactMatches = []
	for key in tqdm(list(storedNames.keys())):
		if storedNames[key]["filtered"] == name: exactMatches.append((key, 0))
		elif storedNames[key]["pronunciation"] == pronunciation: exactMatches.append((key, 0))

	if len(exactMatches) >= 1:
		print("Exact match found!")
		return exactMatches

	# If the name doesn't exist, look for the closest match
	print("Exact match not found, searching for close pronunciations...")
	bestMatches = []
	for nameKey in tqdm(list(storedNames.keys())):
		# Get similatiry score
		score = comparePronunciations(storedNames[nameKey]["pronunciation"], pronunciation)
		# Add to list of best matches
		bestMatches.append((nameKey, score))
		# Once list reaches 10 long, only keep the 10 best matches
		if len(bestMatches) > 10:
			bestMatches = sorted(bestMatches, key=lambda match: match[1], reverse=True)
			bestMatches.pop()

	return bestMatches

def main():
	# Check the pronunciation file of names exists
	assert os.path.isfile("pronunciations.json"), "Couldn't find the pronunciations file!"

	# Get the name to look for
	g2p = G2p()
	name = input("What name would you like to search for?").lower()
	pronunciation = [phone for phone in g2p(name)]

	response = input(f"Does this pronunciation look right? [Y/n]\n{pronunciation}\n")
	# If the algorithm didn't produce the correct pronunciation...
	if response.lower() == "n":
		print("Type each phone and press return. Press return without typing to end")
		print("Type ? for a list of valid phones")
		pronunciation = []
		done = False
		while not done:
			nextPhone = input().upper()
			if nextPhone == "":
				response = input(f"Is this correct? [Y/n]\n{pronunciation}\n")
				# User made a mistake, restart
				if response.lower() == "n":
					pronunciation = []
					print("Resetting...")
				else:
					done = True
			elif nextPhone == "?": print("https://en.wikipedia.org/wiki/ARPABET")
			# Validate input
			elif not isValidPhone(nextPhone): print("Invalid phone")
			else: pronunciation.append(nextPhone)

	# Get the best matches from the list of pronunciations
	bestMatches = getBestMatch(name, pronunciation)
	print(f"Here's the {len(bestMatches)} best matches I found! (in order)")
	for i in bestMatches:
		# Add URL for user friendliness :)
		print(f"https://www.1happybirthday.com/play_song.php?name={i[0]}")

	input("Press return to exit")

if __name__ == "__main__":
	main()
