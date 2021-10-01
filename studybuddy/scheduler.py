from datetime import datetime
from os import environ
from pytz import timezone

from pyairtable.formulas import match

from models import Customer, Offering
from emails import Email, sendEmails
from pairs import getUniqueBuddies, savePairs

now = timezone("Europe/London").localize(datetime.now())
DEBUG = True

############################# EMAIL MONTHLY PAIRS #############################

# Runs 1st day of every month, at xx:xx
if now.day == 1:
	studyBuddies = Customer().all(formula=match({
		'Stage': 'Post SHS',
		'Study Buddy': True,
	}))
	pairs = getUniqueBuddies(studyBuddies)
	savePairs(pairs)

	emails = []
	for pair in pairs:
		for buddy in pair:
			pairIDs = [ human['id'] for human in pair if human['id'] != buddy['id'] ]
			pairParams = "pair1=" + pairIDs[0] + (f"&pair2={pairIDs[1]}" if len(pair) == 3 else "")
			deadline = now.replace(day=8).timestamp()
			rePairLink = f"studybuddy.herokuapp.com/repair?user={ buddy['id'] }&timestamp={ deadline }&{ pairParams }"
			print(rePairLink)

			emails.append(Email(
				to=buddy['fields']['Email-test'],
				templateID=environ.get("SENDGRID_SHS_MONTHLYSTUDYBUDDY_TEMPLATEID"),
				templateData={
					"recordID": buddy['id'],
					"name1": pair[0]['fields']['First Name'],
					"name2": pair[1]['fields']['First Name'],
					"name3": pair[2]['fields']['First Name'] if len(pair) == 3 else '',
					"email1": pair[0]['fields']['Email-test'],
					"email2": pair[1]['fields']['Email-test'],
					"email3": pair[2]['fields']['Email-test'] if len(pair) == 3 else '',
					"rePairLink": rePairLink,
				},
			))
	print(len(emails), 'monthly pairs emails')

	if DEBUG:
		sendEmails(emails[:3])
	else:
		sendEmails(emails)

############################## EMAIL NEW ALUMNI ###############################

# Runs on every end date of Offerings, at xx:xx
offeringsEndingToday = Offering().all(view='Ending today')

offeringsEndingTodayIDs = set(offering['id'] for offering in offeringsEndingToday)
print('Offerings ending today:', [course['fields'].get('Name') for course in offeringsEndingToday])

customers = Customer().all()
emails = []

for customer in customers:
	# if they're not in any courses or already a Study Buddy
	if 'List of Offerings' not in customer['fields'] or customer['fields'].get('Study Buddy'):
		continue
	alumniCourses = offeringsEndingTodayIDs.intersection(customer['fields']['List of Offerings'])
	if len(alumniCourses) > 0:
		print(customer['fields']['First Name'], 'is now an alum')
		emails.append(Email(
			to=customer['fields']['Email-test'],
			templateID=environ.get("SENDGRID_SHS_JOINSTUDYBUDDY_TEMPLATEID"),
			templateData={
				"name": customer['fields']['First Name'],
				"recordID": customer['id'],
			},
		))

print(len(emails), 'invitation emails')

if DEBUG:
	sendEmails(emails[:2])
else:
	sendEmails(emails)


########################### RE-PAIRING AFTER 7 DAYS ###########################

if now.day == 8:
	customers = Customer()
	toBeRePaired = customers.all(formula=match({
		'Stage': 'Post SHS',
		'Study Buddy': True,
		'Re-Pair': True,
	}))
	rePairs = getUniqueBuddies(toBeRePaired, 'Avoid for Re-Pair')

	# reset everyone's re-pair values
	for customer in toBeRePaired:
		customers.update(customer['id'], {
			'Re-Pair': False,
			'Avoid for Re-Pair': [],
		})
	
	emails = []
	# NO PAIRS POSSIBLE
	if len(rePairs) == 0:
		# email every re-pairer there will be no pairs
		for customer in toBeRePaired:
			emails.append(Email(
				to=customer['id'],
				templateID=environ.get('SENDGRID_SHS_NO_REPAIRS_TEMPLATEID'),
				templateData={
					"name": customer['fields']['First Name'],
					"recordID": customer['id'],
				}
			))
	# PAIRS WERE POSSIBLE
	else:
		savePairs(rePairs, 'Avoid for Re-Pair')

		for pair in rePairs:
			for buddy in pair:
				emails.append(Email(
					to=buddy['fields']['Email-test'],
					templateID=environ.get("SENDGRID_SHS_MONTHLYREPAIRS_TEMPLATEID"),
					templateData={
						"recordID": buddy['id'],
						"name1": pair[0]['fields']['First Name'],
						"name2": pair[1]['fields']['First Name'],
						"name3": pair[2]['fields']['First Name'] if len(pair) == 3 else '',
						"email1": pair[0]['fields']['Email-test'],
						"email2": pair[1]['fields']['Email-test'],
						"email3": pair[2]['fields']['Email-test'] if len(pair) == 3 else '',
					},
				))
		print(len(emails), 're-pair emails')

	if DEBUG:
		sendEmails(emails[-2:])
	else:
		sendEmails(emails)


