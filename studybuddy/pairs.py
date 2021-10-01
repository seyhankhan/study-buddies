from json import dumps
from random import shuffle

from pyairtable.formulas import match

from models import Customer


def isNotValidGenderPair(customers, index1, index2):
	gender1 = customers[index1]["fields"]["Gender"]
	gender2 = customers[index2]["fields"]["Gender"]
	preferredGenders1 = customers[index1]["fields"]["Genders To Pair With"]
	preferredGenders2 = customers[index2]["fields"]["Genders To Pair With"]

	return not (gender1 in preferredGenders2 and gender2 in preferredGenders1)

def pairsAreNotValid(customers, invalidPeopleKey):
	# for each pair
	for i in range(0, len(customers) - len(customers) % 2, 2):
		# CHECK IF UNIQUE
		pairID = customers[i + 1]["id"]
		previousPairIDs = customers[i]["fields"].get(invalidPeopleKey)

		if previousPairIDs and pairID in previousPairIDs:
			print(f"NOT UNIQUE: {customers[i+1]['fields']['First Name']} is in {customers[i]['fields']['First Name']}'s list")
			return True

		# CHECK IF MATCHES GENDER PREFERENCES
		if isNotValidGenderPair(customers, i, i + 1):
			print(f"GENDER MISMATCH: {customers[i+1]['fields']['First Name']} and {customers[i]['fields']['First Name']}")
			return True

	# if odd number of people, check the group of 3 is valid
	if len(customers) % 2 == 1:
		# CHECK IF UNIQUE
		id1 = customers[-2]["id"]
		id2 = customers[-3]["id"]
		previousPairIDs = customers[-1]["fields"].get(invalidPeopleKey)

		names = tuple(cust['fields']['First Name'] for cust in customers[-3:])

		if previousPairIDs and (id1 in previousPairIDs or id2 in previousPairIDs):
			print("NOT UNIQUE: %s or %s is in %s's list" % names)
			return True

		# CHECK IF MATCHES GENDER PREFS
		if isNotValidGenderPair(customers, -1, -2) or isNotValidGenderPair(customers, -1, -3):
			print("GENDER MISMATCH: %s or %s and %s" % names)
			return True

	return False


def getUniqueBuddies(participants, invalidPeopleKey='Pairs'):
	turnout = len(participants)
	if turnout < 2:
		return []

	# calculate pairs
	failedShuffles = 0
	while pairsAreNotValid(participants, invalidPeopleKey):
		failedShuffles += 1
		if failedShuffles > 10**7:
			print('10 million failed shuffles...so no pairs at all this month.')
			return []
		shuffle(participants)

	# create a list of every pair group
	pairs = []
	for i in range(0, turnout - turnout % 2, 2):
		pairs.append([ participants[i], participants[i + 1] ])

	# if odd number of people, put the odd guy in the last group
	if turnout % 2 == 1:
		pairs[-1].append(participants[-1])

	print(dumps(
		[[buddy['fields']['First Name'] for buddy in pair] for pair in pairs],
		indent=2
	))
	print("failed shuffle attempts:", failedShuffles)

	return pairs


def savePairs(pairs, invalidPeopleKey='Pairs'):
	customers = Customer()

	for pair in pairs:
		# create hash that links every id in the group to their previous pairs. If no previous pairs, empty list
		invalidPeopleForGroup = {
			buddy['id'] : buddy['fields'][invalidPeopleKey] if invalidPeopleKey in buddy['fields'] else []
				for buddy in pair
		}

		# for each person in this group
		for id in invalidPeopleForGroup:
			# create list of IDs to add to this person's list (everyone thats not him)
			newPairs = [pairID for pairID in invalidPeopleForGroup.keys() if pairID != id]
			# update list of previous pairs
			customers.update(id, {
				invalidPeopleKey: list(set(newPairs + invalidPeopleForGroup[id])),
			})