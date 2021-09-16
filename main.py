########### Seyhan Van Khan
########### Sex Homework Society Study Buddies
########### auto pair people up every month uniquely with monthly prompts
########### September 2021


DEBUG = False

from json import dumps
from os import environ
from random import shuffle

from pyairtable import Table


customersTable = Table(
  environ.get('AIRTABLE_KEY'),
  environ.get('AIRTABLE_SHS_BASE'),
  'Seyhan test copy' if DEBUG else 'Customers'
)

studyBuddies = customersTable.all(view="Study Buddies")
if len(studyBuddies) < 2:
  # TODO
  pass

############################### calculate pairs ################################

def pairsAreUnique(studyBuddies):
  for i in range(0, len(studyBuddies) - len(studyBuddies) % 2, 2):
    pairID = studyBuddies[i+1]['id']
    previousPairIDs = studyBuddies[i]['fields'].get('Pairs')

    if previousPairIDs and pairID in previousPairIDs:
      print(f"NOT UNIQUE: {studyBuddies[i+1]['fields']['First Name']} is in {studyBuddies[i]['fields']['First Name']}'s list")
      return False

  # if odd number of people, check the group of 3 is unique
  if len(studyBuddies) % 2 == 1:
    pair1ID = studyBuddies[-2]['id']
    pair2ID = studyBuddies[-3]['id']
    previousPairIDs = studyBuddies[-1]['fields'].get('Pairs')
    if previousPairIDs and (pair1ID in previousPairIDs or pair2ID in previousPairIDs):
      print(f"NOT UNIQUE: {studyBuddies[-3]['fields']['First Name']} or {studyBuddies[-2]['fields']['First Name']} is in {studyBuddies[-1]['fields']['First Name']}'s list")
      return False

  return True


while not pairsAreUnique(studyBuddies):
  shuffle(studyBuddies)

pairs = []
for i in range(0, len(studyBuddies) - len(studyBuddies) % 2, 2):
  pairs.append([
    studyBuddies[i]['fields']['First Name'],
    studyBuddies[i + 1]['fields']['First Name'],
  ])

# if odd number of people, put the odd guy in the last group
if len(studyBuddies) % 2 == 1:
  pairs[-1].append(studyBuddies[-1]['fields']['First Name'])



print(dumps(pairs, indent=2))
