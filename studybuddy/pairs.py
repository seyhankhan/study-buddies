from json import dumps
from random import shuffle

from models import Customer


def isNotValidGenderPair(customers, index1, index2):
  gender1 = customers[index1]["fields"]["Gender"]
  gender2 = customers[index2]["fields"]["Gender"]
  preferredGenders1 = customers[index1]["fields"]["Genders To Pair With"]
  preferredGenders2 = customers[index2]["fields"]["Genders To Pair With"]

  return not (gender1 in preferredGenders2 and gender2 in preferredGenders1)


def pairsAreNotValid(customers):
  for i in range(0, len(customers) - len(customers) % 2, 2):
    # CHECK IF UNIQUE
    pairID = customers[i + 1]["id"]
    previousPairIDs = customers[i]["fields"].get("Pairs")

    if previousPairIDs and pairID in previousPairIDs:
      print(f"NOT UNIQUE: {customers[i+1]['fields']['First Name']} is in {customers[i]['fields']['First Name']}'s list")
      return True

    # CHECK IF MATCHES GENDER PREFERENCES
    if isNotValidGenderPair(customers, i, i + 1):
      print(f"GENDER MISMATCH: {customers[i+1]['fields']['First Name']} isn't in {customers[i]['fields']['First Name']}'s list")
      return True

  # if odd number of people, check the group of 3 is valid
  if len(customers) % 2 == 1:
    # CHECK IF UNIQUE
    id1 = customers[-2]["id"]
    id2 = customers[-3]["id"]
    previousPairIDs = customers[-1]["fields"].get("Pairs")
    if previousPairIDs and (id1 in previousPairIDs or id2 in previousPairIDs):
      print(f"NOT UNIQUE: {customers[-3]['fields']['First Name']} or {customers[-2]['fields']['First Name']} is in {customers[-1]['fields']['First Name']}'s list")
      return True

    # CHECK IF MATCHES GENDER PREFS
    if isNotValidGenderPair(customers, -1, -2) or isNotValidGenderPair(customers, -1, -3):
      print(f"GENDER MISMATCH: {customers[-3]['fields']['First Name']} or {customers[-2]['fields']['First Name']} isn't in {customers[-1]['fields']['First Name']}'s list")
      return True

  return False


def getUniquePairs():
  studyBuddies = Customer().all(view="Study Buddies")
  if len(studyBuddies) < 2:
    return []

  # calculate pairs
  failedShuffles = 0
  while pairsAreNotValid(studyBuddies):
    failedShuffles += 1
    shuffle(studyBuddies)

	# create a list of every pair group
  pairs = []
  for i in range(0, len(studyBuddies) - len(studyBuddies) % 2, 2):
    pairs.append([
			studyBuddies[i],
			studyBuddies[i + 1],
    ])

  # if odd number of people, put the odd guy in the last group
  if len(studyBuddies) % 2 == 1:
    pairs[-1].append(studyBuddies[-1])

  print(dumps(
		[[buddy['fields']['First Name'] for buddy in pair] for pair in pairs],
		indent=2
  ))
  print("failed shuffle attempts:", failedShuffles)

  return pairs
