from datetime import datetime
from json import dumps
from os import environ
from pytz import timezone

from pyairtable.formulas import match

from models import Customer, Offering
from emails import Email, sendEmails
from pairs import getUniquePairs

now = timezone("UTC").localize(datetime.now())

############################# EMAIL MONTHLY PAIRS #############################

# Runs 1st day of every month, at xx:xx
if now.day == 1:
	pairs = getUniquePairs()
	emails = []
	for pair in pairs:
		for buddy in pair:
			emails.append(Email(
				to=buddy['fields']['Email-test'],
				templateID=environ.get("SENDGRID_SHS_MONTHLYSTUDYBUDDY_TEMPLATEID"),
				templateVariables={
					"recordID": buddy['id'],
					"name1": pair[0]['fields']['First Name'],
					"name2": pair[1]['fields']['First Name'],
					"name3": pair[2]['fields']['First Name'] if len(pair) == 3 else '',
					"email1": pair[0]['fields']['Email-test'],
					"email2": pair[1]['fields']['Email-test'],
					"email3": pair[2]['fields']['Email-test'] if len(pair) == 3 else '',
				},
			))
	print(len(emails), 'monthly pairs emails')

	if settings.DEBUG:
		sendEmails(emails[:2])
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
			templateVariables={
				"name": customer['fields']['First Name'],
				"recordID": customer['id'],
			},
		))

print(len(emails), 'invitation emails')

if settings.DEBUG:
	sendEmails(emails[:2])
else:
	sendEmails(emails)
