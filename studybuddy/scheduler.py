from datetime import datetime
from os import environ
from pytz import timezone

from datetimes import getCurrentDatetime
from emails import Email, sendEmail, sendEmails
from pairs import getUniquePairs

now = timezone("UTC").localize(datetime.now())

############################# EMAIL MONTHLY PAIRS #############################

# Runs 1st day of every month, at xx:xx
if True or now.day == 1:
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
	print(len(emails), 'emails')
	
	sendEmails(emails[:2])
	# sendEmails(emails)
