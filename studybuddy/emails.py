from os import environ

from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendAt


def Email(to, templateID, templateVariables, timestamp=None):
	email = Mail(
		from_email=environ.get("SHS_EMAIL"),
		to_emails=to
	)
	# pass custom values for our HTML placeholders
	email.template_id = templateID
	email.dynamic_template_data = templateVariables

	if timestamp and not settings.DEBUG:
		print(to, timestamp)
		email.send_at = SendAt(timestamp)
	
	return email


def sendEmail(email, sendgridClient=SendGridAPIClient(environ.get("SENDGRID_SHS_KEY"))):
	try:
		response = sendgridClient.send(email)
		print("Sent to:", email.from_email)
		print("Status Code:", response.status_code)
		print("Body:", response.body)
		print("Headers:\n", response.headers)
		return "SENT"
	except Exception as e:
		print(e)
		return "ERROR"


def sendEmails(emails):
	sendgridClient = SendGridAPIClient(environ.get("SENDGRID_SHS_KEY"))
	for email in emails:
		sendEmail(email, sendgridClient)
	print(len(emails), "emails sent")